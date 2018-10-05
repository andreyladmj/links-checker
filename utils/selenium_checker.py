import random

# from utils.proccess_bar_thread import ProccessBarThread
from telnetlib import EC

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import *
from selenium.webdriver.support.wait import WebDriverWait


class SeleniumChecker():
    def __init__(self):
        self.browser = self.create_webdriver()
        # self.browser.manage().timeouts().implicitlyWait(30, TimeUnit.SECONDS);
        self.browser.set_page_load_timeout(60)

    def create_webdriver(self):

        proxy = "http://89.254.142.187:8080"

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--proxy-server=%s' % proxy)
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.add_argument('--start-maximized')
        # chrome_options.add_argument('--start-fullscreen')
        return webdriver.Chrome(
            # 'D:\projects\links-checker\chromedriver.exe',
            'chromedriver',
            service_args=['--disable-cache'],
            chrome_options=chrome_options)

    def get(self, url):
        self.url = url
        self.browser.get(url)

    def find_form(self):
        self.form = self.find_comments_form()
        # self.browser.implicitly_wait(4)

        # delay = 3 # seconds
        # try:
        #     # myElem = WebDriverWait(self.browser, delay).until(EC.presence_of_element_located((By.ID, 'IdOfMyElement')))
        #     myElem = WebDriverWait(self.browser, delay).until(EC.presence_of_element_located(self.form))
        #     print("Page is ready!")
        # except TimeoutException:
        #     print("Loading took too much time!")


        if self.form:
            return True

        return False

    def wait(self):
        self.browser.implicitly_wait(3)

    def unwait(self):
        self.browser.implicitly_wait(0)

    def check_text(self, text):
        return self.browser.page_source.find(text)

    def get_form_fields(self):
        inputs = self.form.find_elements_by_tag_name('input')
        return [input.get_attribute('name') for input in inputs]

    def post_comment(self, **data):
        return self.try_to_fill_all_known_fields(data)

    def submit(self):
        try:
            self.form.find_element_by_name('submit').click()
        except Exception as e:
            self.form.find_element_by_xpath("//input[@type='submit']").click()

    def save_screenshot(self, url):
        name = url.replace(':', '').replace('/', '_')
        self.browser.save_screenshot("/home/andrei/Python/links-checker/tmp/{}.png".format(name))
        return name

    def try_to_fill_all_known_fields(self, data):
        filled = dict()

        for name, val in data.items():
            if self.try_to_fill_field(name, val):
                filled[name] = val

        return filled

    def try_to_fill_field(self, name, message):
        try:
            self.type_to_field_name(name, message)
            return True
        except Exception:
            pass

        return False

    def save_processed_site(self, url, before_submit, after_submit, **kwargs):
        dict_ = kwargs
        dict_['url'] = url
        dict_['before_submit'] = before_submit
        dict_['after_submit'] = after_submit

    def type_to_field_name(self, name, message):
        if self.form:
            comment = self.form.find_element_by_name(name)
        else:
            comment = self.browser.find_element_by_name(name)

        comment.clear()
        comment.send_keys(message)

    def find_comments_form(self):
        forms = self.browser.find_elements_by_tag_name('form')

        if not len(forms):
            raise Exception("Can't find any forms, please check this site")

        for form in forms:
            inputs = form.find_elements_by_tag_name('input')
            all_fields = []

            for input in inputs:
                if input.get_attribute('name') == 'comment_post_ID': # seems it is WP comment form
                    return form

                if input.get_attribute('name') == 'wpdiscuz_unique_id': # seems it is Woocomerce form
                    return form

                if input.get_attribute('name') == 'q': break

                all_fields.append(input.get_attribute('name'))

            if 'email' in all_fields:
                return form

            if 'wc_email' in all_fields:
                return form

        return None


if __name__ == '__main__':
    url = 'https://www.expertselfcare.com/esc-student-covered-by-independent/'
    Comment = SeleniumChecker()
    Comment.get(url)

    if not Comment.find_form():
        print('Form not Found')
        exit(0)

    comment = 'learners can find support with essays'
    author = 'Isabella Arnold'
    email = 'warrenjt1978@yahoo.com'
    acceptor = 'http://www.londonjobsfinder.com/author/audrey-j-hayter'

    data = Comment.post_comment(comment=comment, author=author, email=email, url=acceptor)

    print(data)
