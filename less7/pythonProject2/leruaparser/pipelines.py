# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline

class LeruaparserPipeline:
    def process_item(self, item, spider):
        item['characters'] = self.chracter_process(item['char'], item['value'])
        del item['char']
        del item['value']
        return item

    def chracter_process(self, char, value):
        characters = {}
        for i in range(len(char)):
            characters[char[i]] = value[i].replace(' ', '').replace('\n', '')
        return characters


class LeruaPhotosPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        if item['photos']:
            try:
                for image in item['photos']:
                    yield scrapy.Request(image)
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        item['photos'] = [imp[1] for imp in results if imp[0]]
        return item

