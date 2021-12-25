# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo
from itemadapter import ItemAdapter
from pymongo import MongoClient
from pprint import pprint


class VkparserPipeline:

    def __init__(self):
        self.base = MongoClient('127.0.0.1', 27017)['vkparser']
        self.collection = self.base['vk']
        self.collection.create_index('user_id', unique=True)

    def process_item(self, item, spider):
        check = ['fans', 'friends', 'users_fans']
        for check_point in item.keys():
            if check_point in check:
                break
        print()


        # Тут дополнение с учетом того что база может измениться и к одному человеку могут добавиться еще друзья и фаны.
        # Знаю, что тут нужно улучшить, относительно кода, чтоб можно было дополнять, при изменении количества
        # друзей или фанов или дополения на эти же поля. Я это предусмотрел, через индекс user_id, но еще не сделал, но обязательно сделаю:)
        if self.collection.find_one({'user_id': item['user_id']}) is None:
            self.collection.insert_one(item)
        else:
            self.collection.update_one({'user_id': item['user_id']}, {'$set': {'name': item['name'],
                                                                               'custom_user_link': item['custom_user_link'],
                                                                               'photo': item['photo']},
                                                                      '$addToSet': {check_point: item[check_point][0]}})
        # else:
        #     self.collection.update_one({'user_id': item['user_id']}, {'$set': {item}}, upsert=True)
