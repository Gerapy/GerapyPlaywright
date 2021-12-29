BOT_NAME = 'example'

SPIDER_MODULES = ['example.spiders']
NEWSPIDER_MODULE = 'example.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 5

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'gerapy_playwright.downloadermiddlewares.PlaywrightMiddleware': 543,
}

RETRY_HTTP_CODES = [403, 500, 502, 503, 504]

GERAPY_PLAYWRIGHT_HEADLESS = True

LOG_LEVEL = 'DEBUG'

GERAPY_PLAYWRIGHT_PRETEND = False

GERAPY_PLAYWRIGHT_SCREENSHOT = {
    'type': 'png',
    'full_page': True
}
GERAPY_PLAYWRIGHT_SLEEP = 0

GERAPY_PLAYWRIGHT_DOWNLOAD_TIMEOUT = 10

GERAPY_CHECK_PLAYWRIGHT_INSTALLED = False
