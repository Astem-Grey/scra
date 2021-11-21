import requests
from pprint import pprint
from bs4 import BeautifulSoup
import re

prof = input('Профессия?: ')
size = {'Head Hunter': {'url': 'https://hh.ru',
                        'suff': '/search/vacancy',
                        'params': {'clusters': 'true', 'ored_clusters': 'true', 'enable_snippets': 'true',
                                   'text': prof},
                        'find_all': ('div', {'class': 'vacancy-serp-item__row vacancy-serp-item__row_header'}),
                        'info_prof': ('a', {'class': 'bloko-link', 'data-qa': 'vacancy-serp__vacancy-title'}),
                        'zp': ('span', {'data-qa': 'vacancy-serp__vacancy-compensation',
                                        'class': 'bloko-header-section-3 bloko-header-section-3_lite'}),
                        'error': '\u202f',
                        'further': ('a', {'class': 'bloko-button', 'rel': 'nofollow', 'data-qa': 'pager-next'})
                        },
        'SuperJob': {'url': 'https://russia.superjob.ru',
                     'suff': '/vacancy/search',
                     'params': {'keywords': prof},
                     'find_all': ('div', {'jNMYr GPKTZ _1tH7S'}),
                     'info_prof': ('span', {'class': '_1e6dO _1XzYb _2EZcW'}),
                     'zp': ('span', {'class': '_2Wp8I _1e6dO _1XzYb Js9sN _3Jn4o'}),
                     'error': '\xa0',
                     'further': (
                     'a', {'class': 'icMQ_ bs_sM _3ze9n _1M2AW f-test-button-dalshe f-test-link-Dalshe', 'rel': 'next'})

                     }

        }


sit = size.get('Head Hunter')

# prof = input('Профессия?: ') #replace(' ', '+')

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/95.0.4638.69 Safari/537.36'}

responce = requests.get(sit.get('url') + sit.get('suff'), params=sit.get('params'), headers=header)


result = []

while True:
    dom = BeautifulSoup(responce.text, 'html.parser')

    reque = dom.find_all(sit.get('find_all')[0], sit.get('find_all')[1])
    for element in reque:

        info_prof = element.find(sit.get('info_prof')[0], sit.get('info_prof')[1])
        name_prof = info_prof.getText()

        # Цикл пробегает по детям и вытаскивает ссылку
        for i in info_prof.children:
            try:
                link_prof = info_prof['href']
                break
            except KeyError:
                info_prof = i

        zp1 = []
        zp2 = []
        salary = {}
        zp = element.find(sit.get('zp')[0], sit.get('zp')[1])

        try:
            zp = zp.contents
            zp_clear = zp.count(' ')
            for n in range(zp_clear):
                zp.remove(' ')

            # Тут была попытка сделать универсальность, но столкнулся с проблемой которую не смог решить. Пока не смог.
            # Уточнение внизу

            if zp[0] == 'от ':
                min = float(zp[1].replace(sit.get('error'), ''))
                max = None
            elif zp[0] == 'до ':
                min = None
                max = float(zp[1].replace(sit.get('error'), ''))
            else:
                min, max = zp[0].replace(sit.get('error'), '').replace(' ', '').split('–')
                min = float(min)
                max = float(max)
            valu = (zp[(len(zp) - 1)]).replace('.', '')


        except AttributeError:
            min = None
            max = None
            valu = None
        finally:
            salary = {'min': min, 'max': max, 'valuta': valu}

        info_prof_dict = {'Name_prof': name_prof, 'Prof_link': link_prof, 'Salary': salary, 'Size': sit.get('url')}
        result.append(info_prof_dict)
    try:
        further = dom.find(sit.get('further')[0], sit.get('further')[1])['href']
        url = sit.get('url') + sit.get('further')
        responce = requests.get(url, headers=header)
    except TypeError:
        break

# '<span> <!-- -->—<!-- --> </span>'
# объект class.tag. Вся универсальность полетела к черту из-за того что я не смог обработать данное выражение с сайта SuperJob.
# Буду очень признателен, если в ответе объясните мне как с этим работать. Это вроде строка, но не replace в строке, или remove в списке ее не берет

pprint(result)