# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose

# def processor_users_fans(users):
#     element = []
#     for elem in users:
#         element = element + elem
#     element = list(set(element))
#     print(element)
#     return element


class VkparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field(output_processor=TakeFirst())
    user_id = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(lambda x: int(x)))
    name = scrapy.Field(output_processor=TakeFirst())
    direct_user_link = scrapy.Field(output_processor=TakeFirst())
    custom_user_link = scrapy.Field(output_processor=TakeFirst())
    photo = scrapy.Field(output_processor=TakeFirst())
    friends = scrapy.Field(input_processor=MapCompose(lambda x: int(x)))
    fans = scrapy.Field(input_processor=MapCompose(lambda x: int(x)))
    users_fans = scrapy.Field(input_processor=MapCompose(lambda x: list(set(x))))
    pass
