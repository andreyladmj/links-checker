from collections import Counter
from datetime import datetime
from math import ceil
from os import cpu_count
from random import shuffle
from time import time

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, \
    QVBoxLayout, QGroupBox, QGridLayout, QTextEdit

from utils.file_select import FileSelect
from utils.indexer_site_checker import IndexerSiteChecker
from utils.qlogger import QLogger
from utils.utils import iterate_by_batch, make_xlsx_file


class SpamLink:
    __slots__ = ('url', 'referer', 'count', 'is_redirect', 'status_code', 'redirect_to', 'original_count')

    def __init__(self, url, referer, count, original_count=None):
        self.url = url
        self.referer = referer
        self.count = count
        self.original_count = original_count or count
        self.is_redirect = False
        self.status_code = None
        self.redirect_to = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "{}, {}".format(self.url, self.status_code)


class Indexer(QWidget, FileSelect):

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
        self.files = []
        self.mode = 'indexer'
        self.finished = 0

        self.qlogs = QLogger(self)

        self.logs = []
        self.sites_responses = []
        self.exceptions = []

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.horizontalGroupBox = QGroupBox("Actions")

        self.select_xlsx_button = QPushButton('Select XLSX')
        self.select_xlsx_button.clicked.connect(self.select_xlsx_dialog)

        self.start_process_button = QPushButton('Start Process')
        self.start_process_button.clicked.connect(self.parse_xlsx_files)

        self.export_xlsx_report_button = QPushButton('Export XLSX Report')
        self.export_xlsx_report_button.clicked.connect(self.export_xlsx_report)

        self.export_xlsx_exceptions_report_button = QPushButton('Export Exceptions')
        self.export_xlsx_exceptions_report_button.clicked.connect(self.export_xlsx_exceptions_report)

        self.export_xlsx_redirects_report_button = QPushButton('Export Redirects')
        self.export_xlsx_redirects_report_button.clicked.connect(self.export_xlsx_redirects_report)

        self.fix_indexer_files_button = QPushButton('Fix Indexer Files', self)
        self.fix_indexer_files_button.clicked.connect(self.select_files_for_indexer_fix)

        self.save_fixed_indexer_files_button = QPushButton('Save Fixed Indexer Files', self)
        self.save_fixed_indexer_files_button.clicked.connect(self.save_fixed_indexer_files)

        actions_layout = QGridLayout()
        actions_layout.addWidget(self.select_xlsx_button, 0, 0)
        actions_layout.addWidget(self.start_process_button, 0, 1)
        actions_layout.addWidget(self.export_xlsx_report_button, 0, 2)
        actions_layout.addWidget(self.export_xlsx_exceptions_report_button, 0, 3)
        actions_layout.addWidget(self.export_xlsx_redirects_report_button, 0, 4)
        actions_layout.addWidget(self.fix_indexer_files_button, 1, 0)
        actions_layout.addWidget(self.save_fixed_indexer_files_button, 1, 1)
        self.horizontalGroupBox.setLayout(actions_layout)

        # vbox_layout = QHBoxLayout()
        vbox_layuot = QVBoxLayout()

        for i in range(self.processes):
            hbox_layout = QHBoxLayout()
            parser = IndexerSiteChecker(number=i, parent=self)

            hbox_layout.addWidget(parser.qlabel)
            hbox_layout.addWidget(parser.qbar)
            vbox_layuot.addLayout(hbox_layout)
            self.processes_list.append(parser)

        filterGroupBox = QGroupBox("Filter")

        self.show_all_logs_button = QPushButton('Show All logs')
        self.show_all_logs_button.clicked.connect(self.show_all_logs)

        self.show_all_redirected_button = QPushButton('Show Redirected')
        self.show_all_redirected_button.clicked.connect(self.show_all_redirected)

        self.show_all_exceptions_button = QPushButton('Show Exceptions')
        self.show_all_exceptions_button.clicked.connect(self.show_all_exceptions)

        actions_layout = QGridLayout()
        actions_layout.addWidget(self.show_all_logs_button, 0, 0)
        actions_layout.addWidget(self.show_all_redirected_button, 0, 1)
        actions_layout.addWidget(self.show_all_exceptions_button, 0, 2)
        filterGroupBox.setLayout(actions_layout)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        windowLayout.addLayout(vbox_layuot)
        windowLayout.addWidget(filterGroupBox)
        windowLayout.addWidget(self.qlogs)
        self.setLayout(windowLayout)

        self.show()

    def select_xlsx_dialog(self):
        files = self.openFileNamesDialog()
        if files:
            self.qlogs.log("Selected files {}".format(', '.join(files)))
            self.files = files

    def show_all_logs(self):
        self.qlogs.set_logs(self.qlogs.logs)

    def show_all_redirected(self):
        redirected = []
        for response in self.sites_responses:
            if response.status_code == 301:
                redirected.append("{} redirected to {}\n".format(response.url, response.headers.get('Location')))

        self.qlogs.set_logs(redirected)

    def show_all_exceptions(self):
        exceptions = ["{}: {}".format(exception['site'], exception['exception']) for exception in self.exceptions]
        self.qlogs.set_logs(exceptions)

    def parse_xlsx_files(self):
        self.mode = 'indexer'
        self.start_time = time()
        links = []

        if not len(self.files):
            return self.qlogs.log('Please select file')
        else:
            self.qlogs.log("Starting parse files...")

        for file in self.files:
            links += self.get_links(file)

        self.qlogs.log("Total links: {}".format(len(links)))

        batch_size = ceil(len(links) / self.processes)
        self.qlogs.log('Batch Size: {}'.format(batch_size))
        batches = iterate_by_batch(links, batch_size, None)

        for process, batch in zip(self.processes_list, batches):
            process.set_links(batch)
            process.start()

        # exit_codes = [p.wait() for p in self.processes_list]

    def get_links(self, file, for_checking=False):
        urls = []
        with open(file, 'r') as file:
            for line in file.readlines():
                site, referer, count = line.split(';')
                count = int(count.rstrip())
                original_count = int(count)

                if for_checking:
                    count = 1
                    print('Count', count, original_count)

                urls.append(SpamLink(site, referer, count, original_count))

        shuffle(urls)
        return urls

    def export_xlsx_report(self):
        cnt = Counter()

        for proces in self.processes_list:
            for link in proces.links:
                if link:
                    cnt[link.url] += 1

        self.qlogs.log('Saved as report_statistic.xlsx')
        make_xlsx_file('report_statistic.xlsx', head=['Site', 'Count'], body=cnt.items())

    def export_xlsx_exceptions_report(self):
        report = []
        for exception in self.exceptions:
            report.append([exception['site'], str(exception['exception'])])

        self.qlogs.log('Saved as report_statistic_exceptions.xlsx')
        make_xlsx_file('report_statistic_exceptions.xlsx', head=['Site', 'Exception'], body=report)

    def export_xlsx_redirects_report(self):
        report = []
        for proces in self.processes_list:
            for link in proces.links:
                if link and link.status_code == 301:
                    report.append([link.url, link.redirect_to])

        self.qlogs.log('Saved as report_statistic_redirect.xlsx')
        make_xlsx_file('report_statistic_redirect.xlsx', head=['Site', 'Redirect To'], body=report)

    def select_files_for_indexer_fix(self):
        file = self.openFileNameDialog()
        if file:
            self.qlogs.log("Trying to fix selected file {}".format(file))
            self.fix_indexer_files(file)

    def finish(self):
        self.finished += 1

        if self.finished == self.processes:
            self.qlogs.log('Finished!')
            value = datetime.fromtimestamp(time() - self.start_time)
            self.qlogs.log("Time Execution: {}".format(value.strftime('%H:%M:%S')))

    def save_fixed_indexer_files(self):
        if self.mode != 'fix_file':
            return self.qlogs.log("Sorry, but seems you didn't fix any files")

        filename = self.saveFileDialog()

        if filename:
            saved_links = []

            with open(filename, 'w') as file:
                for response in self.sites_responses:
                    spam_link = response.spam_link

                    if not spam_link.is_redirect and hash(spam_link) not in saved_links:
                        file.write("{};{};{}\n".format(spam_link.url, spam_link.referer, spam_link.original_count))
                        saved_links.append(hash(spam_link))

            self.qlogs.log("Saved {}".format(filename))

    def save_exception(self, object):
        site = object['site']
        exception = object['exception']
        with open('tmp/exceptions.txt', 'w+') as file:
            file.write("{}; {}\n".format(site, str(exception)))

    def fix_indexer_files(self, file):
        self.start_time = time()
        self.mode = 'fix_file'
        links = self.get_links(file, for_checking=True)
        self.qlogs.log("Total links: {}".format(len(links)))
        batch_size = ceil(len(links) / self.processes)
        self.qlogs.log('Batch Size: {}'.format(batch_size))

        batches = iterate_by_batch(links, batch_size, None)

        for process, batch in zip(self.processes_list, batches):
            process.set_links(batch)
            process.start()

        # exit_codes = [p.wait() for p in self.processes_list]
