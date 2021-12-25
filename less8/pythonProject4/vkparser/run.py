from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from vkparser import settings
from vkparser.spiders.vk import VkSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    # Тут хотел вводные добавить, но передумал. Нет необходимости.
    # target = input('Ввести url страничек через запятую')
    # target.split(',')
    process.crawl(VkSpider)

    process.start()
