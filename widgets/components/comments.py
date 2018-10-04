import random

# from utils.proccess_bar_thread import ProccessBarThread
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import *

from utils.proccess_bar_thread import ProccessBarThread
from utils.selenium_checker import SeleniumChecker
from utils.utils import create_selenium_dict_for_form, load_pickle, save_pickle


class QComments(ProccessBarThread):
    def __init__(self, number, parent=None):
        super().__init__()
        self.number = number
        self.tmp_file_name = "tmp/{}.pickl".format(number)
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

        self.processed_donors = []
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

    def try_to_recover(self):
        try:
            data = load_pickle(self.tmp_file_name)

            if data:
                self.sites_with_posted_comments = data
                for row in self.sites_with_posted_comments:
                    next(self.acceptors)
                    self.processed_donors.append(row['donor'])

        except Exception as e:
            pass

        return False

    def donors_loop(self, donors):
        Comment = SeleniumChecker()
        total = len(donors)
        count = 0

        for donor in donors:
            count += 1

            if not donor: continue
            if donor in self.processed_donors: continue

            try:
                Comment.get(donor)

                if not Comment.find_form():
                    self.save_error(donor, 'Form not Found')

                else:
                    comment = random.choice(self.comments)
                    author = random.choice(self.usernames)
                    email = random.choice(self.emails)
                    acceptor = next(self.acceptors)
                    params = create_selenium_dict_for_form(acceptor=acceptor, comment=comment, author=author, email=email)

                    posted_data = Comment.post_comment(**params)
                    screenshot = Comment.save_screenshot(donor)

                    self.processed_donors.append(donor)
                    self.sites_with_posted_comments.append(dict(
                        donor=donor,
                        acceptor=acceptor,
                        comment=comment,
                        author=author,
                        email=email,
                        posted_data=posted_data,
                        screenshot=screenshot,
                    ))
                    save_pickle(self.tmp_file_name, self.sites_with_posted_comments)
            except Exception as e:
                self.save_error(donor, str(e))

    def save_error(self, site, error):
        print(site, error)
        self.sites_with_errors.append({'site': site, 'error': error})

