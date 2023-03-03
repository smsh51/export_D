import requests
from datetime import datetime
from progress.bar import Bar
import atexit
import time
from pandas import DataFrame, read_csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# import sqlite3
# from sqlalchemy import create_engine

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


@atexit.register
def exit_e():
    print('exit divar api app.')


# %% api
def divar_token(**api_data_filter):
    url = 'https://api.divar.ir/v8/search/{}/{}'.format(api_data_filter['json_schema']['cities'][0], api_data_filter['json_schema']['category']['value'])

    headers = {"Content-Type": "application/json"}

    # api_data_filter['last-post-date'] = 1673468493086323  # 3-11-01  # json['last-post-date']

    list_of_tokens = []
    n = 1  # 1_000
    bar = Bar('Loading token {}...'.format(api_data_filter['json_schema']['category']['value']),
              fill='X', max=n, suffix='%(percent).2f%%')

    for i in range(n):
        if bar.index % 10 == 0:
            time.sleep(3)
        bar.next()
        # print(round(i/n * 100, 2), '%')

        try:
            res = requests.post(url, json=api_data_filter, headers=headers, timeout=2)
        except Exception as e:
            api_data_filter['last-post-date'] += 1
            print('except: ', e)
            continue

        if res.status_code == 200:
            data = res.json()
            api_data_filter['last-post-date'] = data['last_post_date']
        else:
            api_data_filter['last-post-date'] += 1
            print('response: ', res.status_code)
            continue

        for widget in data['web_widgets']['post_list']:
            token = widget['data']['token']
            list_of_tokens.append(token)
            # print(token)

        if len(list_of_tokens) - len(set(list_of_tokens)) != 0:
            print('duplicate token.', i, api_data_filter['last-post-date'])
            break

    print(len(list_of_tokens))
    # TODO : write to database
    path_data = './Data/'
    try:
        old_tokens = set(open(path_data + '__tokens__.csv', 'r').read().split('\n'))
    except:
        old_tokens = set([])
    list_of_tokens = set(list_of_tokens) - old_tokens
    return list_of_tokens


# %% export data
class TestExporturlhome():
    def __init__(self):
        self.login = False

    def setup_method(self):
        options = Options()
        options.headless = False
        self.driver = webdriver.Chrome('./driver/chromedriver109.exe', options=options)
        self.vars = {}

    def teardown_method(self):
        self.driver.quit()

    def login(self, number: str = '09303492545'):
        """
        login by sms code.

        Parameters
        ----------
        number : str, optional
            number of login. The default is '09303492545'.

        Returns
        -------
        None.

        """
        try:
            # Test name: login 
            # Step # | name | target | value
            # 1 | open | /s/tehran | 
            self.driver.get("https://divar.ir/s/saveh")
            # 2 | setWindowSize | 1050x708 | 
            self.driver.set_window_size(1050, 708)
            # =========== enter to web site
            # 3 | click | css=.kt-nav-button:nth-child(1) | 
            self.driver.find_element(By.CSS_SELECTOR, ".kt-nav-button:nth-child(1)").click()
            # 4 | mouseOver | css=.kt-button__ripple | 
            login_button_selector = '#app > header > nav > div > div.nav-bar__end-section > div > div > div > button'
            element = self.driver.find_element(By.CSS_SELECTOR, login_button_selector)
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()
            # 5 | click | css=.navbar-my-divar__button-item > .kt-fullwidth-link__title |
            selector = ".navbar-my-divar__button-item > .kt-fullwidth-link__title"
            self.driver.find_element(By.CSS_SELECTOR, selector).click()
            
            # =========== number 
            # 6 | click | id=textfield-lf3abg | 
            input_number_selector = 'body > div.kt-dimmer.kt-dimmer--darker.kt-dimmer--open > div > div > div > div > div > form > div > input'
            self.driver.find_element(By.CSS_SELECTOR, input_number_selector).send_keys(number)
            # 7 | type | id=textfield-lf3abg | 09303492545
            # self.driver.find_element(By.ID, "textfield-7afdep").send_keys(number)
            
            # ========== sms code
            # 8 | click | id=textfield-1bi5o95 | 
            sms_cod_input_selector = 'body > div.kt-dimmer.kt-dimmer--darker.kt-dimmer--open > div > div > div > div > div > form > div > input'
            # enter sms code
            sms_code = input('enter SMS code for login: ')
            self.driver.find_element(By.CSS_SELECTOR, sms_cod_input_selector).send_keys(sms_code)
    
            self.login = True
        except Exception as e:
            print('login Error'.format(e))
            self.login = False
            return
        
        # read and save cookie
        self.cookie = self.driver.get_cookies()
        
        # TODO : check login in divar 
        return 

    # =========================================================  
    def test_exporturlhome(self, url: str, n: int = 100) -> list:
        """
        mining home urls from divar.ir

        Parameters
        ----------
        url : str
            DESCRIPTION.
        n : int, optional
            DESCRIPTION. The default is 100.

        Returns
        -------
        list
            DESCRIPTION.

        """
        # Test name: export_url_home
        # Step # | name | target | value
        # 1 | open | /s/tehran/buy-apartment/mirdamad?districts=72%2C86%2C941&rooms=3&user_type=personal |
        self.driver.get(url)
        time.sleep(5)
        # 2 | setWindowSize | 1011x597 |
        self.driver.set_window_size(1011, 597)
        # 3 | click | css=.post-card-item-af972:nth-child(1) .kt-post-card__body |
        # self.driver.find_element(By.CSS_SELECTOR, ".post-card-item-af972:nth-child(2) .kt-post-card__body")#.click()
        block_selector = '#app > div.kt-col-md-12-d59e3.p-none-e410b.browse-c7458 > main > div > div > div > div'
        home_urls = []
        # blocks.extend(self.driver.find_elements(By.CSS_SELECTOR, block_selector))
        # 4 | runScript | window.scrollTo(0,0) |
        for i in range(int(n)):
            blocks = self.driver.find_elements(By.CSS_SELECTOR, block_selector)

            # export url home
            for block in blocks:
                home_url = block.find_element(By.TAG_NAME, 'a').get_attribute('href').split('/')
                home_url.pop(4)
                home_urls.append('/'.join(home_url))

            self.driver.execute_script("window.scrollTo(0,{})".format((1+i)*1000))
            # sleep rof load page
            time.sleep(2)

        # 5 | close |  |
        # self.driver.close()
        return home_urls

    # =================================================================
    def export_home(self, home_url: str) -> dict:
        """
        give and save data of home from home url

        Parameters
        ----------
        home_url : str
            DESCRIPTION.

        Returns
        -------
        dict
            DESCRIPTION.

        """
        self.driver.get(home_url)
        time.sleep(3)
        home_data = {'date_time': datetime.now(),
                     'url': home_url.split('/')[-1],
                     'active': False,
                     'lat': 0,
                     'lot': 0}

        total_home_selector = '#app > div.container--has-footer-d86a9.kt-container > div > div.kt-row'
        # total_home
        self.driver.find_element(By.CSS_SELECTOR, total_home_selector)

        # ================ save image ================
        source_selector = '#app > div.container--has-footer-d86a9.kt-container > div > div.kt-row > div.kt-col-6.kt-offset-1 > div:nth-child(1) > div > div > div.kt-carousel__slider-wrapper > div.kt-carousel__track > ul > li'
        image_selector = 'div > div > button > picture > source'

        # for all images
        home_data['image_urls'] = []
        for source in self.driver.find_elements(By.CSS_SELECTOR, source_selector):
            image_url = source.find_element(By.CSS_SELECTOR, image_selector).get_attribute('srcset').split('/')
            image_url.pop(5)
            # TODO : save image in database
            home_data['image_urls'].append('/'.join(image_url))

        # ================ quantity image ================
        home_data['quantity_image'] = len(home_data['image_urls'])

        # ================ information ================
        title_selector = '#app > div.container-b6963.kt-container > div > div.kt-row > div.kt-col-5'
        title_selector = '#app > div.container--has-footer-d86a9.kt-container > div > div.kt-row > div.kt-col-5'
        
        infos = self.driver.find_element(By.CSS_SELECTOR, title_selector)

        home_data['title'] = infos.find_elements(By.TAG_NAME, 'div')[2].text.replace('*', '%-%')
        # ================ call  ======================
        if self.login:
            call_selector = '#app > div.container-b6963.kt-container > div > div.kt-row > div.kt-col-5 > div.post-actions > button.kt-button.kt-button--primary.post-actions__get-contact'
            call_selector = '#app > div.container--has-footer-d86a9.kt-container > div > div.kt-row > div.kt-col-5 > div.post-actions > button.kt-button.kt-button--primary.post-actions__get-contact'
            
            self.driver.find_element(By.CSS_SELECTOR, call_selector).click()
            time.sleep(0.7)
            
            call_info_selector = '#app > div.container-b6963.kt-container > div > div.kt-row > div.kt-col-5 > div.expandable-box > div.copy-row > div'
            call_info_selector = '#app > div.container--has-footer-d86a9.kt-container> div > div.kt-row > div.kt-col-5 > div.expandable-box > div.copy-row > div'
            
            try:
                call = self.driver.find_element(By.CSS_SELECTOR, call_info_selector).text.split('\n')
                home_data[call[0]] = call[1]
            except Exception as e:
                print('can not save call info'.format(e))

        # ================ Feature ===================
        info_selector = '#app > div.container--has-footer-d86a9.kt-container > div > div.kt-row > div.kt-col-5 > div:nth-child(4)'
        
        information = self.driver.find_element(By.CSS_SELECTOR, info_selector).text.split('\n')
        for i in range(0, len(information), 2):
            if 'ویژگی' in information[i]:
                home_data['elevator'] = not 'ندارد' in information[i+1]
                home_data['parking'] = not 'ندارد' in information[i+2]
                home_data['warehouse'] = not 'ندارد' in information[i+3]
                break
            if 'آگهی' in information[i]:
                home_data['آژانس املاک'] = information[i+1]
                continue
            home_data[information[i]] = information[i+1]

        # =============== distribution ===================
        desc_selector = '#app > div.container--has-footer-d86a9.kt-container > div > div.kt-row > div.kt-col-5 > div:nth-child(5) > div.kt-base-row.kt-base-row--large.kt-description-row > div > p'
        
        home_data['desc'] = self.driver.find_element(By.CSS_SELECTOR, desc_selector).text.replace('*', '%-%')

        # ================ label =========================
        label_selector = '#app > div.container--has-footer-d86a9.kt-container > div > div.kt-row > div.kt-col-5 > div:nth-child(6)'
        
        home_data['label'] = self.driver.find_element(By.CSS_SELECTOR, label_selector).text.replace('*', '%-%')

        # TODO : simulation home
        # ================================================
        return home_data

    def export_khodro(self, url: str) -> dict:
        self.driver.get(url)
        time.sleep(3)
        data = {'date_time': datetime.now(),
                'url': url.split('/')[-1],
                'active': False,
                'lat': 0,
                'lot': 0}

        total_selector = '#app > div.container-b6963.kt-container > div > div.kt-row'
        total_selector = '#app > div.container--has-footer-d86a9.kt-container > div > div'
        total = self.driver.find_element(By.CSS_SELECTOR, total_selector)

        # ================ save image ================
        source_selector = '#app > div.container--has-footer-d86a9.kt-container > div > div > div.kt-col-6.kt-offset-1 > div:nth-child(1) > div > div > div.kt-carousel__slider-wrapper > div.kt-carousel__track > ul > li'
        image_selector = 'div > div > button > picture > source'

        # for all images
        data['image_urls'] = []
        for source in self.driver.find_elements(By.CSS_SELECTOR, source_selector):
            image_url = source.find_element(By.CSS_SELECTOR, image_selector).get_attribute('srcset').split('/')
            image_url.pop(5)
            # TODO : save image in database
            data['image_urls'].append('/'.join(image_url))

        # ================ quantity image ================
        data['quantity_image'] = len(data['image_urls'])

        # ================ information ================
        title_selector = '#app > div.container-b6963.kt-container > div > div.kt-row > div.kt-col-5'
        title_selector = '#app > div.container--has-footer-d86a9.kt-container > div > div.kt-row > div.kt-col-5'

        infos = self.driver.find_element(By.CSS_SELECTOR, title_selector)

        data['title'] = infos.find_elements(By.TAG_NAME, 'div')[2].text.replace('*', '%-%')
        # ================ call  ======================
        if self.login:
            call_selector = '#app > div.container--has-footer-d86a9.kt-container > div > div.kt-row > div.kt-col-5 > div.post-actions > button.kt-button.kt-button--primary.post-actions__get-contact'

            self.driver.find_element(By.CSS_SELECTOR, call_selector).click()
            time.sleep(0.7)

            call_info_selector = '#app > div.container--has-footer-d86a9.kt-container> div > div.kt-row > div.kt-col-5 > div.expandable-box > div.copy-row > div'

            try:
                call = self.driver.find_element(By.CSS_SELECTOR, call_info_selector).text.split('\n')
                data[call[0]] = call[1]
            except Exception as e:
                print('can not save call info'.format(e))

        # ================ feature ===================
        info_selector = '#app > div.container--has-footer-d86a9.kt-container > div > div > div.kt-col-5 > div:nth-child(6)'

        information = self.driver.find_element(By.CSS_SELECTOR, info_selector).text.split('\n')
        for i in range(0, len(information), 2):
            if 'ویژگی' in information[i]:
                data['elevator'] = not 'ندارد' in information[i + 1]
                data['parking'] = not 'ندارد' in information[i + 2]
                data['warehouse'] = not 'ندارد' in information[i + 3]
                break
            if 'آگهی' in information[i]:
                data['آژانس املاک'] = information[i + 1]
                continue
            data[information[i]] = information[i + 1]

        # =============== distrebution ===================
        desc_selector = '#app > div.container--has-footer-d86a9.kt-container > div > div > div.kt-col-5 > div:nth-child(7)'

        data['desc'] = self.driver.find_element(By.CSS_SELECTOR, desc_selector).text.replace('*', '%-%')

        # ================ label =========================
        label_selector = '#app > div.container--has-footer-d86a9.kt-container > div > div > div.kt-col-5 > div:nth-child(8) > div'

        data['label'] = self.driver.find_element(By.CSS_SELECTOR, label_selector).text.replace('*', '%-%')

        return data


# %% main
def main(s):
    if not s:
        print('license not valid')
        time.sleep(1)
        quit()

    print('start divar api app')
    path_data = './Data/'
    api_data_filter = {'real_estate': {"json_schema": {
                                            "category": {
                                                "value": "real-estate"},
                                            "user_type": {
                                                "value": "شخصی"},
                                            "cities": ["671"]},
                                       "last-post-date": 1676487376650086},

                        'khdro': {"json_schema": {
                                    "category": {
                                        "value": "cars"},
                                    "cities": ["671"]},
                                  "last-post-date": 1676462650748760}}
    tokens_cat = dict()
    test = False
    for category in api_data_filter:
        tokens_cat[category] = divar_token(**api_data_filter[category])

        # for test
        if test:
            break

    self = TestExporturlhome()
    self.setup_method()

    # TODO : input number and handel block number
    # login by default number
    if False:
        self.login()

    category_dict = {'real_estate': self.export_home,
                     'khdro': self.export_khodro}

    for cat in tokens_cat:
        urls = list(map(lambda x: 'https://divar.ir/v/' + x, tokens_cat[cat]))

        df = DataFrame()
        progressbar_max = len(urls)
        print('progressbar :', progressbar_max)
        bar = Bar('Loading {}...'.format(cat), fill='-', max=progressbar_max, suffix='%(percent).2f%%')
        token_export = []

        for url in urls:
            try:
                home_data = category_dict[cat](url)
            except Exception as e:
                print('failed export home data'.format(e))
                continue

            df = df.append(home_data, ignore_index=True)
            token_export.append(url.split('/')[-1])
            bar.next()

        # open old dataframe for append to csv file
        try:
            df_old = read_csv(path_data + '__{}_data__.csv'.format(cat), sep='*')
        except Exception as e:
            print('can not open old df'.format(e))
            df_old = DataFrame(columns=df.columns)

        # write to csv file
        df_old.append(df, ignore_index=True).to_csv(path_data + '__{}_data__.csv'.format(cat), sep='*', index=False)
        print('write to {} csv file.'.format(cat))
        # write token for check old token
        txt_file = open(path_data + '__tokens__.csv', 'a+', encoding='utf8')
        txt_file.write('\n'.join(token_export))
        txt_file.close()
        print('write old tokens')

    # close chrome
    self.teardown_method()

    return True


# %% code
if __name__ == '__main__':
    main(True)
