# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import re

import scrapy
from itemloaders.processors import TakeFirst, MapCompose


def price_processor(price):
    try:
        price = price.replace('\xa0', '')
        price = float(price)
    except ValueError:
        print(price)
    finally:
        return price


def characters_processor(characters):
    char = {}
    for chara in characters:
        a = re.search(r'<dt class="def-list__term">\.+?</dt>', chara)
        a.replace('<dt class="def-list__term">', '').replace('</dt>\n', '')
        b = re.findall(r'<dd class="def-list__definition">\.+?</dd>', chara)
        b.replace('\n', '').replace('<dd class="def-list__definition">', '').replace('</dd>')
        char[a] = b
        characters = char
    return characters

    # characters_temp = {}
    # value = characters.xpath('//dd[@class="def-list__definition"]/text()')
    # characters = characters.xpath('//dt[@class="def-list__term"]//text()')
    # for char, val in characters, value:
    #     if val == '' or val is None:
    #         pass
    #     else:
    #         characters_temp[char] = val
    #
    # return characters_temp



class LeruaparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(price_processor))
    url = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    characters = scrapy.Field()
    char = scrapy.Field()
    value = scrapy.Field()

