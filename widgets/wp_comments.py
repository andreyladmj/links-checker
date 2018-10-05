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
from gevent import monkey
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from utils.cycled_iterator import CycledIterator
from utils.file_select import FileSelect
from utils.indexer_site_checker import IndexerSiteChecker
from utils.qlogger import QLogger
from utils.utils import iterate_by_batch, make_xlsx_file, read_file, read_file_lines
from widgets.components.comments import QComments
from widgets.lcwidget import LCWidget

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

# monkey.patch_all()

class WPComments(LCWidget):

    def __init__(self, parent, number_of_threads):
        super().__init__(parent, number_of_threads)
        self.title = 'WP Comments'

        self.qlogs = QLogger(self)

        self.acceptors_file = 'wp/acceptors.txt'
        self.donors_file = 'wp/donors.txt'
        self.mails_file = 'wp/Mail.txt'
        self.text_comments_file = 'wp/TextComment.txt'
        self.user_names_file = 'wp/UserName.txt'

        self.acceptors = []
        self.donors = []
        self.mails = []
        self.text_comments = []
        self.user_names = []

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        horizontalGroupBox = QGroupBox("Actions")

        self.start_comment_button = QPushButton('Post Comments')
        self.start_comment_button.clicked.connect(self.start_comment)

        actions_layout = QGridLayout()
        actions_layout.addWidget(self.start_comment_button, 0, 0)
        horizontalGroupBox.setLayout(actions_layout)

        self.processesGroupBox = self.getProcessesUI(QComments)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(horizontalGroupBox)
        windowLayout.addLayout(self.processesGroupBox)
        windowLayout.addWidget(self.get_time_execution())
        windowLayout.addWidget(self.qlogs)
        self.setLayout(windowLayout)

        self.show()

    def start_comment(self):
        self.qlogs.log("Starting parse files...")
        self.start_time = time()
        self.read_files()

        self.qlogs.log("Total donors: {}".format(len(self.donors)))

        acceptors = CycledIterator(self.acceptors)

        Comment = QComments(1, self)
        Comment.set_donors(self.donors)
        Comment.set_acceptors(acceptors.get_batch(len(self.donors)))
        Comment.set_emails(self.mails)
        Comment.set_comments(self.text_comments)
        Comment.set_usernames(self.user_names)
        Comment.try_to_recover()
        Comment.donors_loop(self.donors)
        # Comment.start()

    def start_comment_multi(self):
        self.qlogs.log("Starting parse files...")
        self.start_time = time()
        self.read_files()

        self.qlogs.log("Total donors: {}".format(len(self.donors)))

        acceptors = CycledIterator(self.acceptors)

        batch_size = ceil(len(self.donors) / self.processes)
        self.qlogs.log('Batch Size: {}'.format(batch_size))
        batches = iterate_by_batch(self.donors, batch_size, None)

        for process, batch in zip(self.processes_list, batches):
            process.set_donors(batch)
            process.set_acceptors(acceptors.get_batch(len(batch)))
            process.set_emails(self.mails)
            process.set_comments(self.text_comments)
            process.set_usernames(self.user_names)
            process.start()

    def read_files(self):
        self.acceptors = read_file_lines(self.acceptors_file)
        self.donors = read_file_lines(self.donors_file)
        self.mails = shuffle(read_file_lines(self.mails_file))
        self.text_comments = read_file_lines(self.text_comments_file)
        self.user_names = read_file_lines(self.user_names_file)

