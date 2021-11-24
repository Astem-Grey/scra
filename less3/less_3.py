import requests
from pprint import pprint
from bs4 import BeautifulSoup
import re
import time
from random import randint
from pymongo import MongoClient


prof = input('Профессия?: ')
size = {'Head Hunter': {'url': 'https://hh.ru',
                        'suff': '/search/vacancy',
                        'params': {'clusters': 'true', 'ored_clusters': 'true', 'enable_snippets': 'true', 'text': prof,
                                   "area": '113'},
                        'find_all_prem': ('div', {'class': 'vacancy-serp-item vacancy-serp-item_premium',
                                             'data-qa': 'vacancy-serp__vacancy vacancy-serp__vacancy_premium'}),
                        'find_all': ('div', {'class': 'vacancy-serp-item',
                                             'data-qa': 'vacancy-serp__vacancy vacancy-serp__vacancy_standard'}),
                        'info_prof': ('a', {'class': 'bloko-link', 'data-qa': 'vacancy-serp__vacancy-title'}),
                        'zp': ('span', {'data-qa': 'vacancy-serp__vacancy-compensation',
                                        'class': 'bloko-header-section-3 bloko-header-section-3_lite'}),
                        'error_zp': '\u202f',
                        'further': ('a', {'class': 'bloko-button', 'rel': 'nofollow', 'data-qa': 'pager-next'}),
                        'employer': ('a', {'class': 'bloko-link bloko-link_secondary', 'data-qa': 'vacancy-serp__vacancy-employer'}),
                        'error_emp': '\xa0'
                        },
        'SuperJob': {'url': 'https://russia.superjob.ru',
                     'suff': '/vacancy/search',
                     'params': {'keywords': prof, 'noGeo': '1'},
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

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/95.0.4638.69 Safari/537.36'}

responce = requests.get(sit.get('url') + sit.get('suff'), params=sit.get('params'), headers=headers)


base = []
iter = 0


while True:
    start_time = time.time()
    dom = BeautifulSoup(responce.text, 'html.parser')

    reque = dom.find_all(sit.get('find_all')[0], sit.get('find_all')[1]) + dom.find_all(sit.get('find_all_prem')[0], sit.get('find_all_prem')[1])
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
                min = float(zp[1].replace(sit.get('error_zp'), ''))
                max = None
            elif zp[0] == 'до ':
                min = None
                max = float(zp[1].replace(sit.get('error_zp'), ''))
            else:
                min, max = zp[0].replace(sit.get('error_zp'), '').replace(' ', '').split('–')
                min = float(min)
                max = float(max)
            valu = (zp[(len(zp) - 1)]).replace('.', '')


        except AttributeError:
            min = None
            max = None
            valu = None
        finally:
            salary = {'min': min, 'max': max, 'valuta': valu}

        info_employer = element.find(sit.get('employer')[0], sit.get('employer')[1])

        for i in info_employer.children:
            try:
                link_employer = sit.get('url') + info_employer['href']
                name_employer = (''.join(info_employer.contents)).replace(sit.get('error_emp'), '')
                break
            except KeyError:
                info_employer = i

        info_prof_dict = {'Name_prof': name_prof, 'Prof_link': link_prof, 'Salary': salary, 'Size': sit.get('url'),
                          'Employer': name_employer, 'Link_employer': link_employer}
        base.append(info_prof_dict)
        print(info_prof_dict)

    time.sleep(randint(2, 4))
    iter = iter + 1
    # Пришлось таймаутить, а то сайт меня блочил по кд:)
    # Но все равно не все отдает.
    print(f'time {iter} - {time.time() - start_time}')

    try:
        further = dom.find(sit.get('further')[0], sit.get('further')[1])['href']
        url = sit.get('url') + further
        responce = requests.get(url, headers=headers)
    except TypeError:
        print('Больше ничего нет')
        break

client = MongoClient('127.0.0.1', 27017)
db = client['less3']
info_profs = db.profs

for element in base:

    if info_profs.find_one(element) is None:
        info_profs.insert_one(element)
    else:
        pass

a = 150000.0
for i in (info_profs.find({})):
  try:
    sr_min = (i.get('Salary').get('min'))
    sr_max = (i.get('Salary').get('max'))

    if (sr_min <= a <= sr_max) or (sr_max >= a <= sr_min):
      print(i)
  except TypeError:
    if sr_max is None and sr_min is None:
      pass
    else:
      if sr_min is None:
        if sr_max >= a:
          print(i)
      else:
        if sr_min <= a or sr_min <= a:
          print(i)

