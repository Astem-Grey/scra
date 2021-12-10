import time

import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?area=1&fromSearchLine=true&text=Python',
                  'https://hh.ru/search/vacancy?area=1217&area=1932&area=1008&area=1505&area=1817&area=1828&area=1716&area=1511&area=1739&area=1844&area=1192&area=1754&area=1124&area=1463&area=1020&area=1859&area=1943&area=1471&area=1229&area=1661&area=1771&area=1438&area=1146&area=1308&area=1880&area=145&area=1890&area=2019&area=1061&area=1679&area=1051&area=1249&area=1563&search_field=name&search_field=company_name&search_field=description&fromSearchLine=true&text=Python',
                  'https://hh.ru/search/vacancy?area=1202&area=1679&area=1051&area=1249&area=1563&area=1898&area=1575&area=1317&area=1948&area=1090&area=1422&area=1347&area=1118&area=1424&area=1434&area=1553&area=1077&area=1041&area=2114&area=1620&area=1556&area=1174&area=1475&area=1624&search_field=name&search_field=company_name&search_field=description&fromSearchLine=true&text=python&from=suggest_post',
                  'https://hh.ru/search/vacancy?area=2&search_field=name&search_field=company_name&search_field=description&fromSearchLine=true&text=python&from=suggest_post']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@data-qa="pager-next"]//@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)


        links = response.xpath('//a[@data-qa="vacancy-serp__vacancy-title"]//@href').getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, responce: HtmlResponse):
        link_prof = responce.url
        name_prof = responce.xpath('//h1[@data-qa="vacancy-title"]//text()').get()
        salary_prof = responce.xpath('//div[@class="vacancy-salary"]//text()').getall()
        yield JobparserItem(name_prof=name_prof, link_prof=link_prof, salary_prof=salary_prof, url='hh.ru')
