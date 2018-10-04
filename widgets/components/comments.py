import random

# from utils.proccess_bar_thread import ProccessBarThread
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import *

from utils.selenium_checker import SeleniumChecker


class Comments():#ProccessBarThread
    def __init__(self, number, parent=None):
        #super().__init__()
        self.number = number
        self.links = []
        self.processed = 0
        self.total = 0
        self.queue = []
        self.results = []
        self.is_started = False

        self.black_list = []

        # self.response_signal.connect(parent.sites_responses.append)
        # self.exception_signal.connect(parent.save_exception)
        # self.log_signal.connect(parent.qlogs.log)
        # self.finish_signal.connect(parent.finish)

        self.sites_with_posted_comments = []
        self.sites_with_errors = []
        # self.browser = None
        self.browser = self.create_webdriver()

        self.acceptors = []
        self.emails = []
        self.comments = []
        self.usernames = []

    def set_acceptors(self, acceptors):
        self.acceptors = acceptors

    def set_emails(self, emails):
        self.emails = emails

    def set_comments(self, comments):
        self.comments = comments

    def set_usernames(self, usernames):
        self.usernames = usernames

    def create_webdriver(self):

        proxy = "http://89.254.142.187:8080"

        chrome_options = Options()
        # chrome_options.add_argument('--headless')
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

    def donors_loop123(self, donors):
        for donor in donors:
            try:
                self.post_comment(donor)
            except Exception as e:
                self.save_error(donor, str(e))

    def donors_loop(self, donors):
        Comment = SeleniumChecker()

        for donor in donors:
            try:
                Comment.get(donor)
                print('Get {}, #{} of {}'.format(url, count, len(donors)))

                if not Comment.find_form():
                    print('Form not Found on {}'.format(donor))

                else:
                    comment = 'learners can find support with essays'
                    author = 'Isabella Arnold'
                    email = 'warrenjt1978@yahoo.com'
                    acceptor = 'http://www.londonjobsfinder.com/author/audrey-j-hayter'
                    params = create_selenium_dict_for_form(acceptor=acceptor, comment=comment, author=author, email=email)

                    data = Comment.post_comment(**params)
                    Comment.save_screenshot(url)

                    print("Fields")
                    print(Comment.get_form_fields())
                    print('Data:')
                    print(data)
                    print("\n\n")
            except Exception as e:
                print('Exception on {}, {}'.format(url, str(e)))
                print("\n\n")

    def post_comment(self, url):
        self.browser.get(url)
        form = self.find_comments_form()

        if form:
            filled_fileds = self.try_to_fill_all_known_fields(form)
            before_submit = self.save_screenshot(url)
            form.find_element_by_name('submit').click()
            after_submit = self.save_screenshot('{}_after_submit'.format(url))
            self.save_processed_site(url, before_submit, after_submit, **filled_fileds)
        else:
            self.save_error(url, "Can't find comments form")

    def save_screenshot(self, url):
        name = url.replace(':', '').replace('/', '_')
        self.browser.save_screenshot("/home/andrei/Python/links-checker/tmp/{}.png".format(name))
        return name

    def try_to_fill_all_known_fields(self, form):
        filled = dict()

        comment = random.choice(self.comments)
        username = random.choice(self.usernames)
        email = random.choice(self.emails)
        acceptor = random.choice(self.acceptors)

        if self.try_to_fill_field('comment', comment, form=form):
            filled['comment'] = comment

        if self.try_to_fill_field('author', username, form=form):
            filled['username'] = username

        if self.try_to_fill_field('email', email, form=form):
            filled['email'] = email

        if self.try_to_fill_field('url', acceptor, form=form):
            filled['acceptor'] = acceptor

        return filled

    def try_to_fill_field(self, name, message, form=None):
        try:
            self.type_to_field_name(name, message, form=form)
            return True
        except Exception:
            pass

        return False

    def save_processed_site(self, url, before_submit, after_submit, **kwargs):
        dict_ = kwargs
        dict_['url'] = url
        dict_['before_submit'] = before_submit
        dict_['after_submit'] = after_submit

        self.sites_with_posted_comments.append(dict_)

    def save_error(self, site, error):
        print(site, error)
        self.sites_with_errors.append({'site': site, 'error': error})

