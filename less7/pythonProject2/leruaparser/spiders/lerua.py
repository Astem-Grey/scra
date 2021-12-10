import scrapy
from scrapy.http import HtmlResponse
from leruaparser.items import LeruaparserItem
from scrapy.loader import ItemLoader


class LeruaSpider(scrapy.Spider):
    name = 'leroy'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['https://leroymerlin.ru/catalogue/dreli-shurupoverty/']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@data-qa-pagination-item="right"]/@href').get() ## Тут доделать ссылку
        if next_page:
            yield response.follow(('https://leroymerlin.ru' + next_page), callback=self.parse)
        links = response.xpath('//a[@data-qa="product-name"]')
        for link in links:
            yield response.follow(link, callback=self.hand_over)

    def hand_over(self, responce: HtmlResponse):
        loader = ItemLoader(item=LeruaparserItem(), response=responce)
        char = responce.xpath('//dt[@class="def-list__term"]/text()').get()
        loader.add_xpath('name', '//h1[@itemprop="name"]/text()')
        loader.add_xpath('price', '//span[@slot="price"]/text()')
        loader.add_value('url', responce.url)
        loader.add_xpath('photos', '//picture[@slot="pictures"]/source[@media=" only screen and (min-width: 1024px)"]/@srcset')
        # loader.add_xpath('characters', '//div[@class="def-list__group"]')
        loader.add_xpath('char', '//dt[@class="def-list__term"]/text()')
        loader.add_xpath('value', '//dd[@class="def-list__definition"]/text()')
        yield loader.load_item()
