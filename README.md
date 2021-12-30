# Gerapy Playwright

This is a package for supporting Playwright in Scrapy, also this
package is a module in [Gerapy](https://github.com/Gerapy/Gerapy).

## Installation

```shell script
pip3 install gerapy-playwright
playwright install
```

## Usage

You can use `PlaywrightRequest` to specify a request which uses playwright to render.

For example:

```python
yield PlaywrightRequest(detail_url, callback=self.parse_detail)
```

And you also need to enable `PlaywrightMiddleware` in `DOWNLOADER_MIDDLEWARES`:

```python
DOWNLOADER_MIDDLEWARES = {
    'gerapy_playwright.downloadermiddlewares.PlaywrightMiddleware': 543,
}
```

Congratulate, you've finished the all of the required configuration.

If you run the Spider again, Playwright will be started to render every
web page which you configured the request as PlaywrightRequest.

## Settings

GerapyPlaywright provides some optional settings.

### Concurrency

You can directly use Scrapy's setting to set Concurrency of Playwright,
for example:

```python
CONCURRENT_REQUESTS = 3
```

### Pretend as Real Browser

Some website will detect WebDriver or Headless, GerapyPlaywright can
pretend Chromium by inject scripts. This is enabled by default.

You can close it if website does not detect WebDriver to speed up:

```python
GERAPY_PLAYWRIGHT_PRETEND = False
```

Also you can use `pretend` attribute in `PlaywrightRequest` to overwrite this
configuration.

### Logging Level

By default, Playwright will log all the debug messages, so GerapyPlaywright
configured the logging level of Playwright to WARNING.

If you want to see more logs from Playwright, you can change the this setting:

```python
import logging
GERAPY_PLAYWRIGHT_LOGGING_LEVEL = logging.DEBUG
```

### Download Timeout

Playwright may take some time to render the required web page, you can also change this setting, default is `30s`:

```python
# playwright timeout
GERAPY_PLAYWRIGHT_DOWNLOAD_TIMEOUT = 30
```

### Headless

By default, Playwright is running in `Headless` mode, you can also
change it to `False` as you need, default is `True`:

```python
GERAPY_PLAYWRIGHT_HEADLESS = False
```

### Window Size

You can also set the width and height of Playwright window:

```python
GERAPY_PLAYWRIGHT_WINDOW_WIDTH = 1400
GERAPY_PLAYWRIGHT_WINDOW_HEIGHT = 700
```

Default is 1400, 700.

### Proxy

You can set a proxy channel via below this config:

```python
GERAPY_PLAYWRIGHT_PROXY = 'http://tps254.kdlapi.com:15818'
GERAPY_PLAYWRIGHT_PROXY_CREDENTIAL = {
  'username': 'xxx',
  'password': 'xxxx'
}
```

### Screenshot

You can get screenshot of loaded page, you can pass `screenshot` args to `PlaywrightRequest` as dict:

Below are the supported args:

- `type` (str): Specify screenshot type, can be either `jpeg` or `png`. Defaults to `png`.
- `quality` (int): The quality of the image, between 0-100. Not applicable to `png` image.
- `full_page` (bool): When true, take a screenshot of the full scrollable page. Defaults to `False`.
- `clip` (dict): An object which specifies clipping region of the page. This option should have the following fields:
  - `x` (int): x-coordinate of top-left corner of clip area.
  - `y` (int): y-coordinate of top-left corner of clip area.
  - `width` (int): width of clipping area.
  - `height` (int): height of clipping area.
- `omit_background` (bool): Hide default white background and allow capturing screenshot with transparency.
- `timeout` (str): Maximum time in milliseconds, defaults to 30 seconds, pass 0 to disable timeout.

Check more from [https://playwright.dev/python/docs/api/class-page#page-screenshot](https://playwright.dev/python/docs/api/class-page#page-screenshot)。

For example:

```python
yield PlaywrightRequest(start_url, callback=self.parse_index, wait_for='.item .name', screenshot={
            'type': 'png',
            'full_page': True
        })
```

then you can get screenshot result in `response.meta['screenshot']`:

Simplest save it to file:

```python
def parse_index(self, response):
    with open('screenshot.png', 'wb') as f:
        f.write(response.meta['screenshot'].getbuffer())
```

If you want to enable screenshot for all requests, you can configure it by `GERAPY_PLAYWRIGHT_SCREENSHOT`.

For example:

```python
GERAPY_PLAYWRIGHT_SCREENSHOT = {
    'type': 'png',
    'full_page': True
}
```

## PlaywrightRequest

`PlaywrightRequest` provide args which can override global settings above.

- url: request url
- callback: callback
- wait_until: one of "load", "domcontentloaded", "networkidle"
  see [https://playwright.dev/python/docs/api/class-page#page-wait-for-load-state](https://playwright.dev/python/docs/api/class-page#page-wait-for-load-state), default is `domcontentloaded`
- wait_for: wait for some element to load, also supports dict
- script: script to execute
- actions: actions defined for execution of Page object
- proxy: use proxy for this time, like `http://x.x.x.x:x`
- proxy_credential: the proxy credential, like `{'username': 'xxxx', 'password': 'xxxx'}`
- sleep: time to sleep after loaded, override `GERAPY_PLAYWRIGHT_SLEEP`
- timeout: load timeout, override `GERAPY_PLAYWRIGHT_DOWNLOAD_TIMEOUT`
- ignore_resource_types: ignored resource types, override `GERAPY_PLAYWRIGHT_IGNORE_RESOURCE_TYPES`
- pretend: pretend as normal browser, override `GERAPY_PLAYWRIGHT_PRETEND`
- screenshot: ignored resource types, see [https://playwright.dev/python/docs/api/class-page#page-screenshot](https://playwright.dev/python/docs/api/class-page#page-screenshot),
  override `GERAPY_PLAYWRIGHT_SCREENSHOT`

For example, you can configure PlaywrightRequest as:

```python
from gerapy_playwright import PlaywrightRequest

def parse(self, response):
    yield PlaywrightRequest(url,
        callback=self.parse_detail,
        wait_until='domcontentloaded',
        wait_for='title',
        script='() => { return {name: "Germey"} }',
        sleep=2)
```

Then Playwright will:

- wait for document to load
- wait for title to load
- execute `console.log(document)` script
- sleep for 2s
- return the rendered web page content, get from `response.meta['screenshot']`
- return the script executed result, get from `response.meta['script_result']`

For waiting mechanism controlled by JavaScript, you can use await in `script`, for example:

```python
js = '''async () => {
    await new Promise(resolve => setTimeout(resolve, 10000));
    return {
        'name': 'Germey'
    }
}
'''
yield PlaywrightRequest(url, callback=self.parse, script=js)
```

Then you can get the script result from `response.meta['script_result']`, result is `{'name': 'Germey'}`.

If you think the JavaScript is wired to write, you can use actions argument to define a function to execute `Python` based functions, for example:

```python
async def execute_actions(page):
    await page.evaluate('() => { document.title = "Hello World"; }')
    return 1
yield PlaywrightRequest(url, callback=self.parse, actions=execute_actions)
```

Then you can get the actions result from `response.meta['actions_result']`, result is `1`.

Also you can define proxy and proxy_credential for each Reqest, for example:

```python
yield PlaywrightRequest(
  self.base_url,
  callback=self.parse_index,
  priority=10,
  proxy='http://tps254.kdlapi.com:15818',
  proxy_credential={
      'username': 'xxxx',
      'password': 'xxxx'
})
```

`proxy` and `proxy_credential` will override the settings `GERAPY_PLAYWRIGHT_PROXY` and `GERAPY_PLAYWRIGHT_PROXY_CREDENTIAL`.

## Example

For more detail, please see [example](./example).

Also you can directly run with Docker:

```shell
docker run germey/gerapy-playwright-example
```

Outputs:

```shell script
2021-12-27 16:54:14 [scrapy.utils.log] INFO: Scrapy 2.2.0 started (bot: example)
2021-12-27 16:54:14 [scrapy.utils.log] INFO: Versions: lxml 4.7.1.0, libxml2 2.9.12, cssselect 1.1.0, parsel 1.6.0, w3lib 1.22.0, Twisted 21.7.0, Python 3.7.9 (default, Aug 31 2020, 07:22:35) - [Clang 10.0.0 ], pyOpenSSL 21.0.0 (OpenSSL 1.1.1l  24 Aug 2021), cryptography 35.0.0, Platform Darwin-21.1.0-x86_64-i386-64bit
2021-12-27 16:54:14 [scrapy.utils.log] DEBUG: Using reactor: twisted.internet.asyncioreactor.AsyncioSelectorReactor
2021-12-27 16:54:14 [scrapy.crawler] INFO: Overridden settings:
{'BOT_NAME': 'example',
 'CONCURRENT_REQUESTS': 1,
 'NEWSPIDER_MODULE': 'example.spiders',
 'RETRY_HTTP_CODES': [403, 500, 502, 503, 504],
 'SPIDER_MODULES': ['example.spiders']}
2021-12-27 16:54:14 [scrapy.extensions.telnet] INFO: Telnet Password: e931b241390ad06a
2021-12-27 16:54:14 [scrapy.middleware] INFO: Enabled extensions:
['scrapy.extensions.corestats.CoreStats',
 'scrapy.extensions.telnet.TelnetConsole',
 'scrapy.extensions.memusage.MemoryUsage',
 'scrapy.extensions.logstats.LogStats']
2021-12-27 16:54:14 [gerapy.playwright] INFO: playwright libraries already installed
2021-12-27 16:54:14 [scrapy.middleware] INFO: Enabled downloader middlewares:
['scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware',
 'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware',
 'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware',
 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware',
 'gerapy_playwright.downloadermiddlewares.PlaywrightMiddleware',
 'scrapy.downloadermiddlewares.retry.RetryMiddleware',
 'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware',
 'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware',
 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware',
 'scrapy.downloadermiddlewares.cookies.CookiesMiddleware',
 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware',
 'scrapy.downloadermiddlewares.stats.DownloaderStats']
2021-12-27 16:54:14 [scrapy.middleware] INFO: Enabled spider middlewares:
['scrapy.spidermiddlewares.httperror.HttpErrorMiddleware',
 'scrapy.spidermiddlewares.offsite.OffsiteMiddleware',
 'scrapy.spidermiddlewares.referer.RefererMiddleware',
 'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware',
 'scrapy.spidermiddlewares.depth.DepthMiddleware']
2021-12-27 16:54:14 [scrapy.middleware] INFO: Enabled item pipelines:
[]
2021-12-27 16:54:14 [scrapy.core.engine] INFO: Spider opened
2021-12-27 16:54:14 [scrapy.extensions.logstats] INFO: Crawled 0 pages (at 0 pages/min), scraped 0 items (at 0 items/min)
2021-12-27 16:54:14 [scrapy.extensions.telnet] INFO: Telnet console listening on 127.0.0.1:6023
2021-12-27 16:54:14 [example.spiders.movie] DEBUG: start url https://antispider1.scrape.center/page/1
2021-12-27 16:54:14 [gerapy.playwright] DEBUG: processing request <GET https://antispider1.scrape.center/page/1>
2021-12-27 16:54:14 [gerapy.playwright] DEBUG: playwright_meta {'wait_until': 'domcontentloaded', 'wait_for': '.item', 'script': None, 'actions': None, 'sleep': None, 'proxy': None, 'proxy_credential': None, 'pretend': None, 'timeout': None, 'screenshot': None}
2021-12-27 16:54:14 [gerapy.playwright] DEBUG: set options {'headless': False}
cookies []
2021-12-27 16:54:16 [gerapy.playwright] DEBUG: PRETEND_SCRIPTS is run
2021-12-27 16:54:16 [gerapy.playwright] DEBUG: timeout 10
2021-12-27 16:54:16 [gerapy.playwright] DEBUG: crawling https://antispider1.scrape.center/page/1
2021-12-27 16:54:16 [gerapy.playwright] DEBUG: request https://antispider1.scrape.center/page/1 with options {'url': 'https://antispider1.scrape.center/page/1', 'wait_until': 'domcontentloaded'}
2021-12-27 16:54:18 [gerapy.playwright] DEBUG: waiting for .item
2021-12-27 16:54:18 [gerapy.playwright] DEBUG: sleep for 1s
2021-12-27 16:54:19 [gerapy.playwright] DEBUG: taking screenshot using args {'type': 'png', 'full_page': True}
2021-12-27 16:54:19 [gerapy.playwright] DEBUG: close playwright
2021-12-27 16:54:20 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://antispider1.scrape.center/page/1> (referer: None)
2021-12-27 16:54:20 [example.spiders.movie] DEBUG: start url https://antispider1.scrape.center/page/2
2021-12-27 16:54:20 [gerapy.playwright] DEBUG: processing request <GET https://antispider1.scrape.center/page/2>
2021-12-27 16:54:20 [gerapy.playwright] DEBUG: playwright_meta {'wait_until': 'domcontentloaded', 'wait_for': '.item', 'script': None, 'actions': None, 'sleep': None, 'proxy': None, 'proxy_credential': None, 'pretend': None, 'timeout': None, 'screenshot': None}
2021-12-27 16:54:20 [gerapy.playwright] DEBUG: set options {'headless': False}
2021-12-27 16:54:20 [example.spiders.movie] INFO: detail url https://antispider1.scrape.center/detail/1
2021-12-27 16:54:20 [example.spiders.movie] INFO: detail url https://antispider1.scrape.center/detail/2
2021-12-27 16:54:20 [example.spiders.movie] INFO: detail url https://antispider1.scrape.center/detail/3
2021-12-27 16:54:20 [example.spiders.movie] INFO: detail url https://antispider1.scrape.center/detail/4
2021-12-27 16:54:20 [example.spiders.movie] INFO: detail url https://antispider1.scrape.center/detail/5
2021-12-27 16:54:20 [example.spiders.movie] INFO: detail url https://antispider1.scrape.center/detail/6
2021-12-27 16:54:20 [example.spiders.movie] INFO: detail url https://antispider1.scrape.center/detail/7
2021-12-27 16:54:20 [example.spiders.movie] INFO: detail url https://antispider1.scrape.center/detail/8
2021-12-27 16:54:20 [example.spiders.movie] INFO: detail url https://antispider1.scrape.center/detail/9
2021-12-27 16:54:20 [example.spiders.movie] INFO: detail url https://antispider1.scrape.center/detail/10
cookies []
2021-12-27 16:54:21 [gerapy.playwright] DEBUG: PRETEND_SCRIPTS is run
2021-12-27 16:54:21 [gerapy.playwright] DEBUG: timeout 10
2021-12-27 16:54:21 [gerapy.playwright] DEBUG: crawling https://antispider1.scrape.center/page/2
2021-12-27 16:54:21 [gerapy.playwright] DEBUG: request https://antispider1.scrape.center/page/2 with options {'url': 'https://antispider1.scrape.center/page/2', 'wait_until': 'domcontentloaded'}
2021-12-27 16:54:23 [gerapy.playwright] DEBUG: waiting for .item
2021-12-27 16:54:24 [gerapy.playwright] DEBUG: sleep for 1s
2021-12-27 16:54:25 [gerapy.playwright] DEBUG: taking screenshot using args {'type': 'png', 'full_page': True}
2021-12-27 16:54:25 [gerapy.playwright] DEBUG: close playwright
2021-12-27 16:54:25 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://antispider1.scrape.center/page/2> (referer: None)
2021-12-27 16:54:25 [gerapy.playwright] DEBUG: processing request <GET https://antispider1.scrape.center/detail/10>
2021-12-27 16:54:25 [gerapy.playwright] DEBUG: playwright_meta {'wait_until': 'domcontentloaded', 'wait_for': '.item', 'script': None, 'actions': None, 'sleep': None, 'proxy': None, 'proxy_credential': None, 'pretend': None, 'timeout': None, 'screenshot': None}
2021-12-27 16:54:25 [gerapy.playwright] DEBUG: set options {'headless': False}
...
```
