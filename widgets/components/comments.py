import random

# from utils.proccess_bar_thread import ProccessBarThread
from os import getpid

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
        self.tmp_file_name = "../tmp/{}.pickl".format(number)
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
        self.processed_sites = []
        # self.browser = None
        # self.browser = self.create_webdriver()

        self.donors = []
        self.acceptors = []
        self.emails = []
        self.comments = []
        self.usernames = []

    def set_donors(self, donors):
        self.donors = donors

    def set_acceptors(self, acceptors):
        self.acceptors = iter(acceptors)

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
                print('Recovered')
                self.processed_sites = data
                for row in self.processed_sites:
                    print('Checked {}: {}'.format(row['donor'], ('success' if row['success'] else 'fail')))
                    next(self.acceptors)
                    self.processed_donors.append(row['donor'])

        except Exception as e:
            pass

        return False

    def run(self):
        self.try_to_recover()
        self.donors_loop(self.donors)

    def donors_loop(self, donors):
        Comment = SeleniumChecker()
        total = len(donors)
        count = 0

        for donor in donors:
            count += 1

            if not donor: continue
            if donor in self.processed_donors: continue

            try:
                print(getpid(), '{} of {}'.format(count, total), donor)
                Comment.get(donor)

                if not Comment.find_form():
                    self.save_error(donor, 'Form not found')
                else:
                    comment = random.choice(self.comments)
                    author = random.choice(self.usernames)
                    email = random.choice(self.emails)
                    acceptor = next(self.acceptors)

                    posted_data, screenshot_before, screenshot_after = self.post(Comment, donor, acceptor, comment, author, email)

                    while Comment.check_text('You are being asked to login because') != -1:
                        Comment.wait()
                        Comment.get(donor)
                        Comment.find_form()
                        comment = random.choice(self.comments)
                        author = random.choice(self.usernames)
                        email = random.choice(self.emails)
                        posted_data, screenshot_before, screenshot_after = self.post(Comment, donor, acceptor, comment, author, email)
                        Comment.unwait()

                    self.processed_donors.append(donor)
                    self.processed_sites.append(dict(
                        success=True,
                        donor=donor,
                        acceptor=acceptor,
                        comment=comment,
                        author=author,
                        email=email,
                        posted_data=posted_data,
                        screenshot_before=screenshot_before,
                        screenshot_after=screenshot_after,
                    ))
                    save_pickle(self.tmp_file_name, self.processed_sites)
            except Exception as e:
                self.save_error(donor, str(e))

    def post(self, Comment, donor, acceptor, comment, author, email):
        params = create_selenium_dict_for_form(acceptor=acceptor, comment=comment, author=author, email=email)
        posted_data = Comment.post_comment(**params)
        screenshot_before = Comment.save_screenshot(donor+'_1')
        Comment.submit()
        screenshot_after = Comment.save_screenshot(donor+'_2')
        return posted_data, screenshot_before, screenshot_after

    def save_error(self, site, error):
        print('Error', site, error, "\n\n")
        self.processed_sites.append(dict(
            success=False,
            donor=site,
            error=error,
        ))
        save_pickle(self.tmp_file_name, self.processed_sites)

