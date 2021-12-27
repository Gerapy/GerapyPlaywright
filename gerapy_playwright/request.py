from scrapy import Request
import copy


class PlaywrightRequest(Request):
    """
    Scrapy ``Request`` subclass providing additional arguments
    """

    def __init__(self, url, callback=None, wait_until=None, wait_for=None, script=None, actions=None, proxy=None,
                 proxy_credential=None, sleep=None, timeout=None, ignore_resource_types=None, pretend=None, screenshot=None, meta=None,
                 *args, **kwargs):
        """
        :param url: request url
        :param callback: callback
        :param wait_until: one of "load", "domcontentloaded", "networkidle".
                see https://playwright.dev/python/docs/api/class-page#page-wait-for-load-state, default is `domcontentloaded`
        :param wait_for: wait for some element to load, also supports dict
        :param script: script to execute
        :param actions: actions defined for execution of Page object
        :param proxy: use proxy for this time, like `http://x.x.x.x:x`
        :param proxy_credential: the proxy credential, like `{'username': 'xxxx', 'password': 'xxxx'}`
        :param sleep: time to sleep after loaded, override `GERAPY_PLAYWRIGHT_SLEEP`
        :param timeout: load timeout, override `GERAPY_PLAYWRIGHT_DOWNLOAD_TIMEOUT`
        :param ignore_resource_types: ignored resource types, override `GERAPY_PLAYWRIGHT_IGNORE_RESOURCE_TYPES`
        :param pretend: pretend as normal browser, override `GERAPY_PLAYWRIGHT_PRETEND`
        :param screenshot: ignored resource types, see
                https://playwright.dev/python/docs/api/class-page#page-screenshot,
                override `GERAPY_PLAYWRIGHT_SCREENSHOT`
        :param args:
        :param kwargs:
        """
        # use meta info to save args
        meta = copy.deepcopy(meta) or {}
        playwright_meta = meta.get('playwright') or {}

        self.wait_until = playwright_meta.get('wait_until') if playwright_meta.get(
            'wait_until') is not None else (wait_until or 'domcontentloaded')
        self.wait_for = playwright_meta.get('wait_for') if playwright_meta.get(
            'wait_for') is not None else wait_for
        self.script = playwright_meta.get('script') if playwright_meta.get(
            'script') is not None else script
        self.actions = playwright_meta.get('actions') if playwright_meta.get(
            'actions') is not None else actions
        self.sleep = playwright_meta.get('sleep') if playwright_meta.get(
            'sleep') is not None else sleep
        self.proxy = playwright_meta.get('proxy') if playwright_meta.get(
            'proxy') is not None else proxy
        self.proxy_credential = playwright_meta.get('proxy_credential') if playwright_meta.get(
            'proxy_credential') is not None else proxy_credential
        self.pretend = playwright_meta.get('pretend') if playwright_meta.get(
            'pretend') is not None else pretend
        self.timeout = playwright_meta.get('timeout') if playwright_meta.get(
            'timeout') is not None else timeout
        # self.ignore_resource_types = playwright_meta.get('ignore_resource_types') if playwright_meta.get(
        #     'ignore_resource_types') is not None else ignore_resource_types
        self.screenshot = playwright_meta.get('screenshot') if playwright_meta.get(
            'screenshot') is not None else screenshot

        playwright_meta = meta.setdefault('playwright', {})
        playwright_meta['wait_until'] = self.wait_until
        playwright_meta['wait_for'] = self.wait_for
        playwright_meta['script'] = self.script
        playwright_meta['actions'] = self.actions
        playwright_meta['sleep'] = self.sleep
        playwright_meta['proxy'] = self.proxy
        playwright_meta['proxy_credential'] = self.proxy_credential
        playwright_meta['pretend'] = self.pretend
        playwright_meta['timeout'] = self.timeout
        playwright_meta['screenshot'] = self.screenshot
        # playwright_meta['ignore_resource_types'] = self.ignore_resource_types

        super().__init__(url, callback, meta=meta, *args, **kwargs)
