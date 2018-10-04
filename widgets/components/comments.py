import random

# from utils.proccess_bar_thread import ProccessBarThread
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import *

from utils.proccess_bar_thread import ProccessBarThread
from utils.selenium_checker import SeleniumChecker
from utils.utils import create_selenium_dict_for_form


class QComments(ProccessBarThread):
    def __init__(self, number, parent=None):
        super().__init__()
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

        self.donors = []
        self.acceptors = []
        self.emails = []
        self.comments = []
        self.usernames = []

    def set_donors(self, donors):
        self.donors = donors

    def set_acceptors(self, acceptors):
        self.acceptors = acceptors

    def set_emails(self, emails):
        self.emails = emails

    def set_comments(self, comments):
        self.comments = comments

    def set_usernames(self, usernames):
        self.usernames = usernames

    def donors_loop123(self, donors):
        for donor in donors:
            try:
                self.post_comment(donor)
            except Exception as e:
                self.save_error(donor, str(e))

    def donors_loop(self, donors):
        Comment = SeleniumChecker()
        total = len(donors)
        count = 0

        for donor in donors:
            try:
                count += 1
                Comment.get(donor)
                print('Get {}, #{} of {}'.format(donor, count, total))

                if not Comment.find_form():
                    # print('Form not Found on {}'.format(donor))
                    self.save_error(donor, 'Form not Found')

                else:
                    comment = random.choice(self.comments)
                    author = random.choice(self.usernames)
                    email = random.choice(self.emails)
                    acceptor = next(self.acceptors)
                    params = create_selenium_dict_for_form(acceptor=acceptor, comment=comment, author=author, email=email)

                    posted_data = Comment.post_comment(**params)
                    screenshot = Comment.save_screenshot(donor)

                    self.sites_with_posted_comments.append(dict(
                        donor=donor,
                        params=params,
                        posted_data=posted_data,
                        screenshot=screenshot,
                    ))

                    # print("Fields")
                    # print(Comment.get_form_fields())
                    # print('Data:')
                    # print(data)
                    # print("\n\n")
            except Exception as e:
                self.save_error(donor, str(e))

    def save_processed_site(self, url, before_submit, after_submit, **kwargs):
        dict_ = kwargs
        dict_['url'] = url
        dict_['before_submit'] = before_submit
        dict_['after_submit'] = after_submit

        self.sites_with_posted_comments.append(dict_)

    def save_error(self, site, error):
        print(site, error)
        self.sites_with_errors.append({'site': site, 'error': error})

