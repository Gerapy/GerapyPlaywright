import asyncio
import sys
import urllib.parse
import twisted.internet
from io import BytesIO
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from scrapy.http import HtmlResponse
from scrapy.utils.python import global_object_name
from twisted.internet.asyncioreactor import AsyncioSelectorReactor
from twisted.internet.defer import Deferred
from gerapy_playwright.pretend import SCRIPTS as PRETEND_SCRIPTS
from gerapy_playwright.settings import *
from gerapy_playwright.utils import install_playwright, is_playwright_installed
from playwright._impl._api_types import Error as PlaywrightError

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

reactor = AsyncioSelectorReactor(asyncio.get_event_loop())

# install AsyncioSelectorReactor
twisted.internet.reactor = reactor
sys.modules['twisted.internet.reactor'] = reactor


def as_deferred(f):
    """
    transform a Twisted Deffered to an Asyncio Future
    :param f: async function
    """
    return Deferred.fromFuture(asyncio.ensure_future(f))


logger = logging.getLogger('gerapy.playwright')


class PlaywrightMiddleware(object):
    """
    Downloader middleware handling the requests with Puppeteer
    """

    def _retry(self, request, reason, spider):
        """
        get retry request
        :param request:
        :param reason:
        :param spider:
        :return:
        """
        if not self.retry_enabled:
            return

        retries = request.meta.get('retry_times', 0) + 1
        retry_times = self.max_retry_times

        if 'max_retry_times' in request.meta:
            retry_times = request.meta['max_retry_times']

        stats = spider.crawler.stats
        if retries <= retry_times:
            logger.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust

            if isinstance(reason, Exception):
                reason = global_object_name(reason.__class__)

            stats.inc_value('retry/count')
            stats.inc_value('retry/reason_count/%s' % reason)
            return retryreq
        else:
            stats.inc_value('retry/max_reached')
            logger.error("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})

    @classmethod
    def from_crawler(cls, crawler):
        """
        init the middleware
        :param crawler:
        :return:
        """
        settings = crawler.settings
        logging_level = settings.get(
            'GERAPY_PLAYWRIGHT_LOGGING_LEVEL', GERAPY_PLAYWRIGHT_LOGGING_LEVEL)
        # logging.getLogger('websockets').setLevel(logging_level)
        logging.getLogger('playwright').setLevel(logging_level)

        cls.check_playwright_installed = settings.get(
            'GERAPY_CHECK_PLAYWRIGHT_INSTALLED', GERAPY_CHECK_PLAYWRIGHT_INSTALLED)

        if cls.check_playwright_installed:
            playwright_installed = is_playwright_installed()
            if not playwright_installed:
                logger.info(
                    'playwright libraries not installed, start to install')
                install_playwright()
            else:
                logger.info('playwright libraries already installed')

        # init settings
        cls.window_width = settings.get(
            'GERAPY_PLAYWRIGHT_WINDOW_WIDTH', GERAPY_PLAYWRIGHT_WINDOW_WIDTH)
        cls.window_height = settings.get(
            'GERAPY_PLAYWRIGHT_WINDOW_HEIGHT', GERAPY_PLAYWRIGHT_WINDOW_HEIGHT)
        cls.default_user_agent = settings.get('GERAPY_PLAYWRIGHT_DEFAULT_USER_AGENT',
                                              GERAPY_PLAYWRIGHT_DEFAULT_USER_AGENT)
        cls.headless = settings.get(
            'GERAPY_PLAYWRIGHT_HEADLESS', GERAPY_PLAYWRIGHT_HEADLESS)
        cls.channel = settings.get(
            'GERAPY_PLAYWRIGHT_CHANNEL', GERAPY_PLAYWRIGHT_CHANNEL)
        cls.slow_mo = settings.get(
            'GERAPY_PLAYWRIGHT_SLOW_MO', GERAPY_PLAYWRIGHT_SLOW_MO)
        # cls.ignore_default_args = settings.get('GERAPY_PLAYWRIGHT_IGNORE_DEFAULT_ARGS',
        #                                        GERAPY_PLAYWRIGHT_IGNORE_DEFAULT_ARGS)
        # cls.handle_sigint = settings.get(
        #     'GERAPY_PLAYWRIGHT_HANDLE_SIGINT', GERAPY_PLAYWRIGHT_HANDLE_SIGINT)
        # cls.handle_sigterm = settings.get(
        #     'GERAPY_PLAYWRIGHT_HANDLE_SIGTERM', GERAPY_PLAYWRIGHT_HANDLE_SIGTERM)
        # cls.handle_sighup = settings.get(
        #     'GERAPY_PLAYWRIGHT_HANDLE_SIGHUP', GERAPY_PLAYWRIGHT_HANDLE_SIGHUP)
        cls.devtools = settings.get(
            'GERAPY_PLAYWRIGHT_DEVTOOLS', GERAPY_PLAYWRIGHT_DEVTOOLS)
        cls.executable_path = settings.get(
            'GERAPY_PLAYWRIGHT_EXECUTABLE_PATH', GERAPY_PLAYWRIGHT_EXECUTABLE_PATH)
        cls.disable_extensions = settings.get('GERAPY_PLAYWRIGHT_DISABLE_EXTENSIONS',
                                              GERAPY_PLAYWRIGHT_DISABLE_EXTENSIONS)
        cls.hide_scrollbars = settings.get(
            'GERAPY_PLAYWRIGHT_HIDE_SCROLLBARS', GERAPY_PLAYWRIGHT_HIDE_SCROLLBARS)
        cls.mute_audio = settings.get(
            'GERAPY_PLAYWRIGHT_MUTE_AUDIO', GERAPY_PLAYWRIGHT_MUTE_AUDIO)
        cls.no_sandbox = settings.get(
            'GERAPY_PLAYWRIGHT_NO_SANDBOX', GERAPY_PLAYWRIGHT_NO_SANDBOX)
        cls.disable_setuid_sandbox = settings.get('GERAPY_PLAYWRIGHT_DISABLE_SETUID_SANDBOX',
                                                  GERAPY_PLAYWRIGHT_DISABLE_SETUID_SANDBOX)
        cls.disable_gpu = settings.get(
            'GERAPY_PLAYWRIGHT_DISABLE_GPU', GERAPY_PLAYWRIGHT_DISABLE_GPU)
        cls.download_timeout = settings.get('GERAPY_PLAYWRIGHT_DOWNLOAD_TIMEOUT',
                                            settings.get('DOWNLOAD_TIMEOUT', GERAPY_PLAYWRIGHT_DOWNLOAD_TIMEOUT))
        # cls.ignore_resource_types = settings.get('GERAPY_PLAYWRIGHT_IGNORE_RESOURCE_TYPES',
        #                                          GERAPY_PLAYWRIGHT_IGNORE_RESOURCE_TYPES)
        cls.screenshot = settings.get(
            'GERAPY_PLAYWRIGHT_SCREENSHOT', GERAPY_PLAYWRIGHT_SCREENSHOT)
        cls.pretend = settings.get(
            'GERAPY_PLAYWRIGHT_PRETEND', GERAPY_PLAYWRIGHT_PRETEND)
        cls.sleep = settings.get(
            'GERAPY_PLAYWRIGHT_SLEEP', GERAPY_PLAYWRIGHT_SLEEP)
        # cls.enable_request_interception = settings.getbool('GERAPY_ENABLE_REQUEST_INTERCEPTION',
        #                                                    GERAPY_ENABLE_REQUEST_INTERCEPTION)
        cls.retry_enabled = settings.getbool('RETRY_ENABLED')
        cls.max_retry_times = settings.getint('RETRY_TIMES')
        cls.retry_http_codes = set(int(x)
                                   for x in settings.getlist('RETRY_HTTP_CODES'))
        cls.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')
        cls.proxy = settings.get('GERAPY_PLAYWRIGHT_PROXY')
        cls.proxy_credential = settings.get(
            'GERAPY_PLAYWRIGHT_PROXY_CREDENTIAL')
        return cls()

    async def _process_request(self, request, spider):
        """
        use playwright to process spider
        :param request:
        :param spider:
        :return:
        """
        # get playwright meta
        playwright_meta = request.meta.get('playwright') or {}
        logger.debug('playwright_meta %s', playwright_meta)
        if not isinstance(playwright_meta, dict) or len(playwright_meta.keys()) == 0:
            return

        options = {
            'headless': self.headless,
            'args': [],
        }
        if self.executable_path is not None:
            options['executablePath'] = self.executable_path
        if self.slow_mo is not None:
            options['slowMo'] = self.slow_mo
        if self.devtools is not None:
            options['devtools'] = self.devtools
        if self.channel is not None:
            options['channel'] = self.channel
        # if self.ignore_default_args is not None:
        #     options['ignoreDefaultArgs'] = self.ignore_default_args
        # if self.handle_sigint:
        #     options['handleSIGINT'] = self.handle_sigint
        # if self.handle_sigterm:
        #     options['handleSIGTERM'] = self.handle_sigterm
        # if self.handle_sighup:
        #     options['handleSIGHUP'] = self.handle_sighup
        if self.disable_extensions is not None:
            options['args'].append('--disable-extensions')
        if self.hide_scrollbars is not None:
            options['args'].append('--hide-scrollbars')
        if self.mute_audio is not None:
            options['args'].append('--mute-audio')
        if self.no_sandbox is not None:
            options['args'].append('--no-sandbox')
        if self.disable_setuid_sandbox is not None:
            options['args'].append('--disable-setuid-sandbox')
        if self.disable_gpu is not None:
            options['args'].append('--disable-gpu')

        # pretend as normal browser
        _pretend = self.pretend  # get global pretend setting
        if playwright_meta.get('pretend') is not None:
            # get local pretend setting to overwrite global
            _pretend = playwright_meta.get('pretend')

        # set proxy and proxy credential
        _proxy = self.proxy
        if playwright_meta.get('proxy') is not None:
            _proxy = playwright_meta.get('proxy')
        if _proxy:
            options['proxy'] = {
                'server': _proxy
            }
        _proxy_credential = self.proxy_credential
        if playwright_meta.get('proxy_credential') is not None:
            _proxy_credential = playwright_meta.get('proxy_credential')
        if _proxy_credential and _proxy:
            options['proxy'].update(_proxy_credential)

        logger.debug('set options %s', options)

        # set default user_agent
        _user_agent = self.default_user_agent
        # get Scrapy request ua, exclude default('Scrapy/2.5.0 (+https://scrapy.org)')
        if 'Scrapy' not in request.headers.get('User-Agent').decode():
            _user_agent = request.headers.get(
                'User-Agent').decode()

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(**options)

            context = await browser.new_context(
                viewport={'width': self.window_width,
                        'height': self.window_height},
                user_agent=_user_agent
            )

            # set cookies
            parse_result = urllib.parse.urlsplit(request.url)
            domain = parse_result.hostname
            _cookies = []
            if isinstance(request.cookies, dict):
                _cookies = [{'name': k, 'value': v, 'domain': domain, 'path': '/'}
                            for k, v in request.cookies.items()]
            else:
                for _cookie in _cookies:
                    if isinstance(_cookie, dict) and 'domain' not in _cookie.keys():
                        _cookie['domain'] = domain
                    if isinstance(_cookie, dict) and 'path' not in _cookie.keys():
                        _cookie['path'] = '/'
            if len(_cookies):
                await context.add_cookies(_cookies)

            page = await context.new_page()

            if _pretend:
                logger.debug('try to pretend webdriver for url %s', request.url)
                for script in PRETEND_SCRIPTS:
                    await page.add_init_script(script=script)

            # # the headers must be set using request interception
            # await page.setRequestInterception(self.enable_request_interception)

            # if self.enable_request_interception:
            #     @page.on('request')
            #     async def _handle_interception(pu_request):
            #         # handle headers
            #         overrides = {
            #             'headers': pu_request.headers
            #         }
            #         # handle resource types
            #         _ignore_resource_types = self.ignore_resource_types
            #         if request.meta.get('playwright', {}).get('ignore_resource_types') is not None:
            #             _ignore_resource_types = request.meta.get(
            #                 'playwright', {}).get('ignore_resource_types')
            #         if pu_request.resourceType in _ignore_resource_types:
            #             await pu_request.abort()
            #         else:
            #             await pu_request.continue_(overrides)

            # set timeout
            _timeout = self.download_timeout
            if playwright_meta.get('timeout') is not None:
                _timeout = playwright_meta.get('timeout')
            # timeout is `ms` instead of `s`, so need to multiply 1000
            page.set_default_timeout(_timeout * 1000)

            logger.debug('crawling %s', request.url)

            response = None
            try:
                options = {
                    'url': request.url
                }
                if playwright_meta.get('wait_until'):
                    options['wait_until'] = playwright_meta.get('wait_until')
                logger.debug('request %s with options %s', request.url, options)
                response = await page.goto(**options)
            except (PlaywrightTimeoutError, PlaywrightError):
                logger.exception(
                    'error rendering url %s using playwright', request.url, exc_info=True)
                await page.close()
                await browser.close()
                return self._retry(request, 504, spider)

            # wait for dom loaded
            if playwright_meta.get('wait_for'):
                _wait_for = playwright_meta.get('wait_for')
                try:
                    logger.debug('waiting for %s of url %s',
                                _wait_for, request.url)
                    if isinstance(_wait_for, dict):
                        await page.wait_for_selector(**_wait_for)
                    else:
                        await page.wait_for_selector(_wait_for)
                except PlaywrightTimeoutError:
                    logger.error('error waiting for %s of %s',
                                _wait_for, request.url)
                    await page.close()
                    await browser.close()
                    return self._retry(request, 504, spider)

            _actions_result = None
            # evaluate actions
            if playwright_meta.get('actions'):
                _actions = playwright_meta.get('actions')
                logger.debug('evaluating %s', _actions)
                _actions_result = await _actions(page)

            _script_result = None
            # evaluate script
            if playwright_meta.get('script'):
                _script = playwright_meta.get('script')
                logger.debug('evaluating %s', _script)
                _script_result = await page.evaluate(_script)

            # sleep
            _sleep = self.sleep
            if playwright_meta.get('sleep') is not None:
                _sleep = playwright_meta.get('sleep')
            if _sleep is not None and _sleep is not 0:
                logger.debug('sleep for %ss of url %s', _sleep, request.url)
                await asyncio.sleep(_sleep)

            content = await page.content()

            # screenshot
            _screenshot = self.screenshot
            if playwright_meta.get('screenshot') is not None:
                _screenshot = playwright_meta.get('screenshot')
            screenshot = None
            if _screenshot:
                logger.debug('taking screenshot using args %s of url %s',
                            _screenshot, request.url)
                screenshot = await page.screenshot(**_screenshot)
                if isinstance(screenshot, bytes):
                    screenshot = BytesIO(screenshot)

            # close page and browser
            logger.debug('close playwright of url %s', request.url)
            await page.close()
            await browser.close()

            if not response:
                logger.error(
                    'get null response by playwright of url %s', request.url)

            # Necessary to bypass the compression middleware
            headers = response.headers
            headers.pop('content-encoding', None)
            headers.pop('Content-Encoding', None)

            response = HtmlResponse(
                page.url,
                status=response.status,
                headers=response.headers,
                body=content,
                encoding='utf-8',
                request=request
            )
            if _script_result:
                response.meta['script_result'] = _script_result
            if _actions_result:
                response.meta['actions_result'] = _actions_result
            if screenshot:
                response.meta['screenshot'] = screenshot
            return response

    def process_request(self, request, spider):
        """
        process request using playwright
        :param request:
        :param spider:
        :return:
        """
        logger.debug('processing request %s', request)
        return as_deferred(self._process_request(request, spider))

    async def _spider_closed(self):
        pass

    def spider_closed(self):
        """
        callback when spider closed
        :return:
        """
        return as_deferred(self._spider_closed())
