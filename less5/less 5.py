from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
from datetime import datetime, timedelta
import time
import re
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['less5']
mails = db.mails

def convert_datetime(inp):
    ### Функция примитивненько приводит к виду более менее обычной даты.
    check = inp.split(',')[0]
    if (re.search(r'\d\d\s\w+', inp)) is not None:
        check = 'comp'

    dic = {'Сегодня': inp.replace('Сегодня', f'{datetime.now().date()}'),
           'Вчера': inp.replace('Вчера', f'{datetime.now().date() - timedelta(days=1)}'),
           'comp': inp.replace(',', f' {datetime.now().year},')}
    tim = dic.get(check)
    return tim


link_elem = []
list_links = []
list_links_page = []
mess_data = []
info_message = {}


options = Options()
options.add_argument('--start-maximized')

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(10)
driver.get('https://mail.ru/')

login = driver.find_element_by_xpath("//input[contains(@class,'email-input')]")
login.send_keys('study.ai_172@mail.ru')
login.send_keys(Keys.ENTER)
password = driver.find_element_by_xpath("//input[contains(@class,'password-input')]")
password.send_keys('NextPassword172#')
password.send_keys(Keys.ENTER)

mail_area = driver.find_element_by_xpath('//div[@class="draggable"]')
mail_links = mail_area.find_elements_by_xpath('.//a[contains(@class, "llc js-tooltip-direction_letter-bottom")]')
while True:
    try:
        list_links_page.clear()
        for element in mail_links:
            list_links_page.append(element.get_attribute('href'))

        result_list = list(set(list_links_page) - set(list_links))

        for elem in result_list:
            elem = elem.replace('https://e.mail.ru', '')
            elem = driver.find_element_by_xpath(f'//a[@href="{elem}"]').get_attribute('href')

            if elem is not list_links:
                list_links.append(elem)
                link_mess = elem.replace('https://e.mail.ru', '')
                mess_link = driver.find_element_by_xpath(f'//a[@href="{link_mess}"]').click()
                try:
                    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "scrollable_content")))
                    author_email = driver.find_element_by_xpath('//span[contains(@class, "letter-contact")]').get_attribute('title')
                    author_name = driver.find_element_by_xpath('//span[contains(@class, "letter-contact")]').text

                    text_message = driver.find_element(By.CLASS_NAME, 'letter__body').text
                    tema = driver.find_element(By.CLASS_NAME, 'thread__subject-line').text
                    date = driver.find_element(By.CLASS_NAME, 'letter__date').text
                    date = convert_datetime(date)
                    all_dict = {'author_name': author_name, 'author_email': author_email, 'tema': tema,
                                'text_message': text_message, 'date': date}
                except TimeoutException:
                    print('Страница не прогрузилась')
                    continue

                if mails.find_one(all_dict) is None:
                    mails.insert_one(all_dict)
                else:
                    pass

                driver.back()
                print(elem)
                time.sleep(2)

        mail_area = driver.find_element_by_xpath('//div[@class="draggable"]')
        mail_links = mail_area.find_elements_by_xpath('.//a[contains(@class, "llc js-tooltip-direction_letter-bottom")]')
        ## Тут такое наваял из-за того что столкнлся с этой ошибкой StaleElementReferenceException. Ну в общем кое-как ее обошел
        ## Ближе к концу написания программы понял, как обойти толее элегантно, но уже поздновато было:)
        (mail_links[-1]).send_keys(Keys.PAGE_DOWN)
        mail_area = driver.find_element_by_xpath('//div[@class="draggable"]')
        mail_links = mail_area.find_elements_by_xpath('.//a[contains(@class, "llc js-tooltip-direction_letter-bottom")]')



        if len(result_list) == 0:
            break
    except NoSuchElementException:
        action = ActionChains(driver)
        butt = driver.find_element_by_xpath('//button[@data-test-id="checkPhoneActive-yes"]')
        action.click(butt)
        action.perform()
