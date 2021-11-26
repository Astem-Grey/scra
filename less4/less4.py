import requests
from lxml import html
from pprint import pprint
import re
from datetime import datetime
from pymongo import MongoClient

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/95.0.4638.69 Safari/537.36'}

size_news = {'Lenta': {
    'url': 'https://lenta.ru',
    'spots': {'//div[@class="span8 js-main__content"]': './/div[@class="item"]',
              '//div[@class="b-yellow-box__wrap"]': './/div[@class="item"]'},
    'next_data': {'datetime': '//time[@class="g-date"]//@datetime'},
    'error': '\xa0'
},
    'Mail': {
        'url': 'https://news.mail.ru',
        'spots': {'//div[@class="js-module" and @data-module="TrackBlocks"]': './/div[contains(@class,"daynews__item")]',
                  '//ul[@class="list list_type_square list_half js-module"]': './/li[@class="list__item"]'},
        'next_data': {'datetime': '//span[@class="note__text breadcrumbs__text js-ago"]//@datetime',
                      'source_link': './/a[contains(@class, "link") and contains(@class,"breadcrumbs__link")]//@href',
                      'source': './/a[contains(@class, "link") and contains(@class,"breadcrumbs__link")]//text()'},
        'error': '\xa0'
    },
    # 'Yandex': {
    #     'url': 'https://yandex.ru/news',
    #     'spots': {'//div[contains(@class,"mg-grid__col_xs_12")]': './/a[@class="mg-card__link"]'},
    #     'error': '\xa0',
    #     'next_data': {'time': './/a[@class="mg-card__source-link"//span[@class="mg-card-source__time"]/text()',
    #                   'source': './/a[@class="mg-card__source-link"//text()'}
    #          }
}

size = size_news['Mail']
responce = requests.get(size['url'], headers=headers)
all_new = {}

dom = html.fromstring(responce.text)

reque = size.get('spots')
data_base = []

for spot, step in reque.items():
    element = dom.xpath(spot)
    for target in element:
        target_spot = target.xpath(step)
        for result in target_spot:
            link = result.xpath('.//@href')
            name = result.xpath('.//text()')

            if (re.search('https://', link[0])) is not None:
                link = link[0]
            else:
                link = size['url'] + link[0]

            for el in name:
                try:
                    name = datetime.strftime(el)
                except TypeError:
                    name = el.replace(size.get('error'), ' ')

            all_new['name'] = name
            all_new['link'] = link

            responce2 = requests.get(link, headers=headers)
            dom2 = html.fromstring(responce2.text)
            # while True:
            #     responce2 = requests.get(source, headers=headers)
            #     dom2 = html.fromstring(responce2.text)
            #     source = dom2.xpath(f'//a[contains(text(),"{name1[0]}")]/.//@href')
            #     print(source)
            #     if len(source) != 0:
            #         source = source[0]
            #         all_new['source_link'] = source
            #     else:
            #         break

            try:
                next_data = size['next_data']
                for name, el in next_data.items():
                    elem = dom2.xpath(el)
                    try:
                        try:
                            elem = elem[0]
                            elem = elem.split('+')
                            elem = elem[0]
                            elem = datetime.strptime(elem, '%Y-%m-%dT%H:%M:%S')
                        except IndexError:
                            elem = "Левый сайт, времени нет или ссылка на видео"
                    except ValueError:
                        continue
                    finally:
                        all_new.update({name: elem})
            except KeyError:
                continue
            finally:
                print(all_new)
                data_base.append(all_new)

client = MongoClient('127.0.0.1', 27017)
db = client['less4']
news = db.news

for element in data_base:
    if news.find_one(element) is None:
        news.insert_one(element)
    else:
        pass