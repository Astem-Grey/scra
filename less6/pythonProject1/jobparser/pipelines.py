# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
import pandas as pd

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class JobparserPipeline:
    def __init__(self):
        self.mongo_base = MongoClient('127.0.0.1', 27017)['jobbase']

    def process_item(self, item, spider):
        final_salary = self.finaly_salary(item['salary_prof'])
        item['min_salary'] = final_salary[0]
        item['max_salary'] = final_salary[1]
        item['currency'] = final_salary[2]
        del item['salary_prof']
        collections = self.mongo_base[spider.name]
        if collections.find_one(item) is None:
            collections.insert_one(item)
        self.save_to_pd_scv(collections.find())

        return item

    def finaly_salary(self, salary):
        minim = None
        maxim = None
        val = None
        try:
            salary.remove(' ')
            if len(salary) == 4:
                if salary[0] == 'от ':
                    minim = float(salary[1].replace('\xa0', ''))
                    maxim = None
                    val = salary[2]
                elif salary[0] == 'до ':
                    minim = None
                    maxim = float(salary[1].replace('\xa0', ''))
                    val = salary[2]
            elif len(salary) == 6:
                minim = float(salary[1].replace('\xa0', ''))
                maxim = float(salary[3].replace('\xa0', ''))
                val = salary[4]
        except ValueError:
            pass

        return minim, maxim, val

    def save_to_pd_scv(self, base):
        df = pd.DataFrame(list(base))
        df.to_csv('out.csv', index=False, mode='a')
