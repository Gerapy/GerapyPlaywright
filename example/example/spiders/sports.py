import scrapy
from gerapy_playwright import PlaywrightRequest


class SportsSpider(scrapy.Spider):
    name = 'sports'
    allowed_domains = ['sports.qq.com']
    start_urls = ['http://sports.qq.com/']

    def start_requests(self):
        for url in self.start_urls:
            yield PlaywrightRequest(url, callback=self.parse_index, pretend=False)

    def parse_index(self, response):
        pass
