import random
from collections import Counter
from datetime import datetime
from math import ceil
from os import cpu_count
from random import shuffle
from time import time

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, \
    QVBoxLayout, QGroupBox, QGridLayout, QTextEdit, QLabel, QProgressBar
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from utils.file_select import FileSelect
from utils.indexer_site_checker import IndexerSiteChecker
from utils.qlogger import QLogger
from utils.utils import iterate_by_batch, make_xlsx_file

'''
Исходные данные:
Есть база с донорами URL страницы: donors.txt
Есть база акцепторов, текст для заполнения поля Website : acceptors.txt
Есть текст для заполнения поля Name: UserName.txt
Есть текст для заполнения поля Email: Mail.txt
Есть текст для заполнения поля Comment: TextComment.txt

Система такая: 

Нужно на странице донора заполнить поля:

Website из файла acceptors.txt 
Name из файла UserName.txt  
Email из файла Mail.txt  
Comment из файла TextComment.txt  

И отправить на сабмит кнопкой: Post Comment
'''


class WPComments(QWidget, FileSelect):

    def __init__(self, parent):
        super().__init__()
        self.title = 'Indxer'
        self.left = 10
        self.top = 50
        self.width = 1024
        self.height = 840
        self.parent = parent
        self.processes = cpu_count()
        self.processes_list = []

        self.acceptors = self.read_file('wp/acceptors.txt')
        self.donors = self.read_file('wp/donors.txt')
        self.mails = self.read_file('wp/Mail.txt')
        self.text_comments = self.read_file('wp/TextComment.txt')
        self.user_names = self.read_file('wp/UserName.txt')

        self.browser = self.create_webdriver()

        self.initUI()

    def read_file(self, fname):
        with open(fname) as f:
            return f.readlines()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.horizontalGroupBox = QGroupBox("Actions")

        self.post_comments_button = QPushButton('Post Comments')
        self.post_comments_button.clicked.connect(self.post_comments)

        actions_layout = QGridLayout()
        actions_layout.addWidget(self.post_comments_button, 0, 0)
        self.horizontalGroupBox.setLayout(actions_layout)

        # vbox_layuot = QVBoxLayout()
        # self.bars = {}
        #
        # for i in range(self.processes):
        #     hbox_layout = QHBoxLayout()
        #     parser = IndexerSiteChecker(number=i, parent=self)
        #
        #     bar = QProgressBar(self)
        #     bar.setMaximum(100)
        #     bar.setMinimum(0)
        #
        #     self.bars[i] = {
        #         'label': QLabel('Process: {}'.format(i), self),
        #         'bar': bar,
        #     }
        #
        #     parser.set_bar_updating_bar_func(self.bars[i]['bar'].setValue, self.bars[i]['label'].setText)
        #
        #     hbox_layout.addWidget(self.bars[i]['label'])
        #     hbox_layout.addWidget(self.bars[i]['bar'])
        #
        #     vbox_layuot.addLayout(hbox_layout)
        #     self.processes_list.append(parser)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        # windowLayout.addWidget(self.qlogs)
        self.setLayout(windowLayout)

        self.show()

    def create_webdriver(self):
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome(
            'chromedriver',
            service_args=['--disable-cache'],
            chrome_options=chrome_options)

    def type_to_field_name(self, name, message):
        comment = self.browser.find_element_by_name(name)
        comment.clear()
        comment.send_keys(message)

    def post_comments(self):
        # url = self.donors[0]
        # acceptor = random.choice(self.acceptors)
        # mail = random.choice(self.mails)
        # text_comment = random.choice(self.text_comments)
        # user_name = random.choice(self.user_names)

        total = len(self.donors)

        for url in self.donors:
            try:
                self.browser.get(url)
                form = self.get_comments_form()
                names = self.get_input_names(form)
                print(url, names)
            except Exception as e:
                print("URL: {} has some troubles! trace: {}".format(url, str(e)))


        return

        for url in self.donors:
            self.browser.get(url)

            try:
                el = self.browser.find_element_by_name('comment')
                el = self.browser.find_element_by_name('author')
                el = self.browser.find_element_by_name('email')
                el = self.browser.find_element_by_name('url')
                el = self.browser.find_element_by_name('submit')
            except:
                print("URL: {} has some troubles!".format(url))

        # el = self.browser.find_element_by_name('comment')
        # print(el)
        # print(dir(el))
        #
        # print('IIIII')
        # el = self.browser.find_element_by_name('commentjoawdhawd')
        # print(el)
        # print(dir(el))

        # type_to_field_name("comment", "I like it !!")
        # type_to_field_name("author", "Udel Baranov")
        # type_to_field_name("email", "otjer.mamonov@gmail.com")
        # type_to_field_name("url", "tri-dnya-v-zapoe.com")
        # submit = browser.find_element_by_name('submit')

    def get_comments_form(self):
        forms = self.browser.find_elements_by_tag_name('form')

        for form in forms:
            inputs = form.find_elements_by_tag_name('input')
            all_fields = []

            for input in inputs:
                if input.get_attribute('name') == 'q': break
                all_fields.append(input.get_attribute('name'))

            if 'submit' in all_fields:
                return form

        return None

    def get_input_names(self, form):
        inputs = form.find_elements_by_tag_name('input')
        names = []

        for input in inputs:
            names.append(input.get_attribute('name'))

        return names