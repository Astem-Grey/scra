import scrapy
from vkparser.items import VkparserItem
from scrapy.loader import ItemLoader
from scrapy.http import HtmlResponse
from scrapy_selenium import SeleniumRequest
from scrapy import Selector
import re
from pprint import pprint


class VkSpider(scrapy.Spider):
    name = 'vk'
    allowed_domains = ['vk.com']
    start_urls = ['https://vk.com/']
    target_urls = ['/s.lyubakov2']
    # target_urls = ['/zxcnbzxn', '/id36497884', '/reginavasilchuk']
    user_fans = []

    def start_requests(self):

        """Заходим на стартовую страничку"""

        if not self.start_urls and hasattr(self, 'start_url'):
            raise AttributeError(
                "Crawling could not start: 'start_urls' not found "
                "or empty (but found 'start_url' attribute instead, "
                "did you miss an 's'?)")
        for url in self.start_urls:
            yield scrapy.Request(url=url, meta={'dont_redirect': True})

    def parse(self, responce: HtmlResponse):

        """Собираем данные для авторизации. И сама авторизация. К сожалению почти все регулярки"""

        hash = check_perem('hash', responce.text)
        ip_h = re.search(r"ip_h: '\w+'", responce.text)[0]
        ip_h = ip_h.split(':')[1]
        ip_h = ip_h.replace("'", '').replace(' ', '')
        lg_domain_h = re.search(r'name="lg_domain_h" value="\w+"', responce.text)[0]
        lg_domain_h = lg_domain_h.split('=')[2]
        lg_domain_h = lg_domain_h.replace('"', '')
        to = re.search(r'"to":"\w+"', responce.text)[0]
        to = to.split(':')[1]
        to = to.replace('"', '')
        return scrapy.FormRequest(url='https://login.vk.com/?act=login',
                                  method='POST',
                                  formdata={
                                      'act': 'login',
                                      'role': 'al_frame',
                                      'expire': '',
                                      'to': to,
                                      'recaptcha': '',
                                      'captcha_sid': '',
                                      'captcha_key': '',
                                      '_origin': 'https://vk.com',
                                      'ip_h': ip_h,
                                      'lg_domain_h': lg_domain_h,
                                      'ul': '',
                                      'email': '+79858789339',
                                      'pass': 'Warnen22'
                                  },
                                  callback=self.auth_step_two)

    def auth_step_two(self, responce: HtmlResponse):

        """Важные переменные, пусть и неиспользованные. Ну и главная страничка пользователя"""

        # Эти переменные не понадобились, но они кое где в процессе используются, так что не стал их убирать.
        key = check_perem('key', responce.text)
        uid = check_perem('uid', responce.text)
        token = check_perem('token', responce.text)

        yield responce.follow(url='https://vk.com/feed',
                              meta={'dont_redirect': True},
                              callback=self.gooo)

    def gooo(self, responce: HtmlResponse):

        """Переключение на страницу цели:) Ну и добавление ее данных в базу"""

        for target in self.target_urls:
            yield responce.follow(url=target,
                                  meta={'dont_redirect': True},
                                  callback=self.user_parce)


    def user_parce(self, responce: HtmlResponse):

        """Отправка первого запроса о фанах и друзьях"""

        user_id = responce.xpath('//a[@data-task-click="ProfileAction/abuse"]//@data-user_id').get()
        # fans = responce.xpath(f'''//a[@onclick="return page.showPageMembers(event, {user_id}, 'fans');"]//text()''').getall()   #  Количество фанов
        # friends = responce.xpath(f"""//a[@onclick="return page.showPageMembers(event, {user_id}, 'friends');"]/@href""").get()  # Ссылка на страницу списка друзей
        target_users_contact = []
        payload = {'act': 'box', 'al': '1', 'boxhash': '', 'oid': user_id, 'tab': 'fans'}
        yield scrapy.FormRequest(url='https://vk.com/al_page.php?act=box',
                                 method='POST',
                                 formdata=payload,
                                 callback=self.contact,
                                 cb_kwargs={'contact': ['fans', user_id], 'users_fans': target_users_contact})
        payload2 = {'act': 'box', 'al': '1', 'instance': '0.6503571078517387', 'oid': user_id, 'part': '1', 'tab': 'friends'}
        target_users_contact = []
        yield scrapy.FormRequest(url=f'https://vk.com/al_page.php?act=box&oid={user_id}',
                                 method='POST',
                                 formdata=payload2,
                                 callback=self.contact,
                                 cb_kwargs={'contact': ['friends', user_id], 'users_fans': target_users_contact})


    def contact(self, responce: HtmlResponse, contact, users_fans):

        """Получение списка ссылок и маркер необходимости итерации дальше. Отправка на сбор данных со страницы
        И снова сбор пользователей"""

        users_links, count = get_users_link(responce.text)
        if contact[0] == 'fans':
            self.user_fans.append(users_links)


        for user_link in users_links:
            yield responce.follow(url=user_link,
                                  meta={'dont_redirect': True},
                                  callback=self.get_item,
                                  cb_kwargs={'contact': contact})

        if count:
            payload = {'act': 'box', 'al': '1', 'offset': count[0], 'oid': contact[1], 'tab': contact[0]}
            yield scrapy.FormRequest(url='https://vk.com/al_page.php?act=box',
                                     method='POST',
                                     callback=self.contact,
                                     formdata=payload,
                                     cb_kwargs={'contact': contact})
        else:
            # Знаю что не правильно готовить item в пауке, но не придумал, как обновлять список в уже готовом item
            yield responce.follow(url=f'https://vk.com/id{contact[1]}',
                                  meta={'dont_redirect': True},
                                  callback=self.get_item,
                                  cb_kwargs={'contact': ['users_fans', self.user_fans]})




    # def friends(self, responce: HtmlResponse, friend):
    #     print()
    #     for user_link in get_users_link(responce.text):
    #         yield responce.follow(url=user_link,
    #                               callback=self.get_item,
    #                               cb_kwargs={'friend': friend})

        # sel = responce.text
        # sel = sel.replace('\\\\\\', '').replace('\\\\', '').replace('\\', '')
        # # user_item = re.findall(r'<div class="fans_fanph_wrap ".+?</div>', sel, re.DOTALL)
        # user_link = re.findall(r'href="\S+">n', sel)

    def get_item(self, responce: HtmlResponse, contact):

        """Сбор данных со страниц. Логика по user_id для заблокированных, подозрительных и удаленнх страниц. Данные с них не собираем"""

        loader = ItemLoader(item=VkparserItem(), response=responce)

        # direct_user_link = responce.xpath('//meta[@property="og:url"]/@content').get()
        user_id = responce.xpath('//a[@data-task-click="ProfileAction/abuse"]//@data-user_id').get()
        loader.add_value('user_id', user_id)
        if user_id:
            loader.add_value('custom_user_link', responce.url)
            loader.add_value('direct_user_link', f'https://vk.com/id{user_id}')
            loader.add_value(contact[0], contact[1])
            loader.add_xpath('photo', '//img[@class="page_avatar_img"]/@src') # Там же можно было и вытащить полноразмерное фото, но я не стал. Смысла особого не было
            loader.add_xpath('name', '//h1[@class="page_name"]/text()')
            yield loader.load_item()
        else:
            pass




# def status_get_item(responce):
#     sel = responce.replace('\\\\\\', '').replace('\\\\', '').replace('\\', '')



def get_users_link(responce):

    """Функция обработки ответа и сбора ссылок на пользовательские страницы. Тут же забираю маркер для итерации"""

    sel = responce.replace('\\\\\\', '').replace('\\\\', '').replace('\\', '')
    users_link = re.findall(r'href="/\w+', sel)
    user_link_commit = []
    error = ['/v']
    for user_link in users_link:
        if user_link not in error:
            user_link = user_link.replace('href="', '').replace('"', '')
            user_link_commit.append(user_link)
    users_link = user_link_commit

    try:
        numb = re.search(r'\d+,true', sel)[0]
        numb = numb.split(',')
    except TypeError:
        numb = False
    return users_link, numb


def check_perem(perm, resp):
    perm = re.search(f'"{perm}":"\S+"', resp)[0]
    perm = perm.split(':')[1]
    perm = perm.replace('"', '')
    return perm


