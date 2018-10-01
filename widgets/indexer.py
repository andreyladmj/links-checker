from collections import Counter
from datetime import datetime
from math import ceil
from os import cpu_count
from random import shuffle
from time import time

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, \
    QVBoxLayout, QGroupBox, QGridLayout, QTextEdit, QLabel, QProgressBar, QCheckBox, QLineEdit

from utils.file_select import FileSelect
from utils.indexer_site_checker import IndexerSiteChecker
from utils.qlogger import QLogger
from utils.utils import iterate_by_batch, make_xlsx_file
from widgets.components.spam_link import SpamLink
from widgets.lcwidget import LCWidget


class Indexer(LCWidget):

    def __init__(self, parent, number_of_threads):
        super().__init__(parent, number_of_threads)
        self.title = 'Indxer'
        self.files = []
        self.mode = 'indexer'
        self.use_upper_limit = False

        self.logs = []
        self.sites_responses = []
        self.exceptions = []

        self.update_thread_info_counter = 0
        self.initUI()

    def _update_status(self):
        if self.start_time:
            self.update_execution_time()
            self.update_thread_info_counter += 1

            if self.update_thread_info_counter > 10:
                self.update_thread_info_counter = 0

                for proc in self.processes_list:
                    if proc.is_started:
                        proc.update_info()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.init_timer()

        settingsGroupBox = self.getSettingsUI()
        horizontalGroupBox = self.getActionsUI()
        filterGroupBox = self.getFilterUI()
        self.processesGroupBox = self.getProcessesUI(IndexerSiteChecker)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(settingsGroupBox)
        windowLayout.addWidget(horizontalGroupBox)
        windowLayout.addLayout(self.processesGroupBox)
        windowLayout.addWidget(self.get_time_execution())
        windowLayout.addWidget(filterGroupBox)
        windowLayout.addWidget(self.qlogs)
        self.setLayout(windowLayout)

        self.show()

    def getProcessesUI(self, test=None):
        vbox_layuot = QVBoxLayout()
        self.bars = {}

        for i in range(self.processes):
            hbox_layout = QHBoxLayout()
            parser = IndexerSiteChecker(number=i, parent=self)

            bar = QProgressBar(self)
            bar.setMaximum(100)
            bar.setMinimum(0)

            self.bars[i] = {
                'label': QLabel('Process: {}'.format(i), self),
                'bar': bar,
            }

            parser.set_bar_updating_bar_func(self.bars[i]['bar'].setValue, self.bars[i]['label'].setText)

            hbox_layout.addWidget(self.bars[i]['label'])
            hbox_layout.addWidget(self.bars[i]['bar'])

            vbox_layuot.addLayout(hbox_layout)
            self.processes_list.append(parser)

        return vbox_layuot

    def getSettingsUI(self):
        settingsGroupBox = QGroupBox("Settings")
        settingsGridLayout = QGridLayout()
        self.upper_limit_checkbox = QCheckBox("Use upper limit", self)
        self.upper_limit_checkbox.stateChanged.connect(self.change_upper_limit_state)

        self.settings_upper_limit = QLineEdit()
        self.settings_upper_limit.setValidator(QIntValidator(0, 100000))
        self.settings_upper_limit.setMaximumWidth(50)

        settingsGridLayout.addWidget(self.upper_limit_checkbox, 0, 0)
        settingsGridLayout.addWidget(self.settings_upper_limit, 0, 1)
        settingsGroupBox.setLayout(settingsGridLayout)
        return settingsGroupBox

    def getActionsUI(self):
        horizontalGroupBox = QGroupBox("Actions")

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
        horizontalGroupBox.setLayout(actions_layout)
        return horizontalGroupBox

    def getFilterUI(self):
        filterGroupBox = QGroupBox("Filter")

        self.show_all_logs_button = QPushButton('Show All logs')
        self.show_all_logs_button.clicked.connect(self.show_all_logs)

        self.show_all_redirected_button = QPushButton('Show Redirects')
        self.show_all_redirected_button.clicked.connect(self.show_all_redirected)

        self.show_all_exceptions_button = QPushButton('Show Exceptions')
        self.show_all_exceptions_button.clicked.connect(self.show_all_exceptions)

        actions_layout = QGridLayout()
        actions_layout.addWidget(self.show_all_logs_button, 0, 0)
        actions_layout.addWidget(self.show_all_redirected_button, 0, 1)
        actions_layout.addWidget(self.show_all_exceptions_button, 0, 2)
        filterGroupBox.setLayout(actions_layout)
        return filterGroupBox

    def select_xlsx_dialog(self):
        files = self.openFileNamesDialog()
        if files:
            self.qlogs.log("Selected files {}".format(', '.join(files)))
            self.files = files

    def show_all_logs(self):
        self.qlogs.set_logs(self.qlogs.logs)

    def show_all_redirected(self):
        redirected = []

        for proces in self.processes_list:
            for link in proces.links:
                if link and link.is_redirect:
                    redirected.append("{} redirected to {}\n".format(link.url, link.redirect_to))

        self.qlogs.set_logs(redirected)

    def show_all_exceptions(self):
        exceptions = ["{}: {}".format(exception['site'], exception['exception']) for exception in self.exceptions]
        self.qlogs.set_logs(exceptions)

    def parse_xlsx_files(self):
        self.mode = 'indexer'
        links = []

        if not len(self.files):
            return self.qlogs.log('Please select file')

        self.qlogs.log("Starting parse files...")
        self.start_time = time()

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

                if not line.strip(): continue

                try:
                    site, referer, count = line.split(';')
                except Exception as e:
                    self.qlogs.log("\nParsing file error:")
                    self.qlogs.log(str(e))
                    self.qlogs.log("Line: {}\n".format(line))
                    continue

                site = site.rstrip()
                referer = referer.rstrip()
                count = int(count.rstrip())
                original_count = int(count)

                if self.use_upper_limit and self.settings_upper_limit.text():
                    count = int(self.settings_upper_limit.text())

                if for_checking:
                    count = 1

                urls.append(SpamLink(site, referer, count, original_count))

        shuffle(urls)
        return urls

    def export_xlsx_report(self):
        cnt = Counter()
        for proces in self.processes_list:
            for link in proces.links:
                if link:
                    cnt[link.url] += link.get_requests_count()

        file = self.saveFileDialog('report_statistic.xlsx')
        if file:
            self.qlogs.log("Saving to {} file".format(file))
            make_xlsx_file(file, head=['Site', 'Count'], body=cnt.items())
            self.qlogs.log("Saved!")

    def export_xlsx_exceptions_report(self):
        report = []
        for exception in self.exceptions:
            report.append([exception['site'], str(exception['exception'])])

        file = self.saveFileDialog(name='report_statistic_exceptions.xlsx')
        if file:
            self.qlogs.log("Saving to {} file".format(file))
            make_xlsx_file(file, head=['Site', 'Exception'], body=report)
            self.qlogs.log("Saved!")

    def export_xlsx_redirects_report(self):
        report = []

        for proces in self.processes_list:
            for link in proces.links:
                if link and link.is_redirect:
                    report.append([link.url, link.redirect_to])

        file = self.saveFileDialog(name='report_statistic_redirect.xlsx')
        if file:
            self.qlogs.log("Saving to {} file".format(file))
            make_xlsx_file(file, head=['Site', 'Redirect To'], body=report)
            self.qlogs.log("Saved!")

    def select_files_for_indexer_fix(self):
        file = self.openFileNameDialog()
        if file:
            self.qlogs.log("Trying to fix selected file {}".format(file))
            self.fix_indexer_files(file)

    def save_fixed_indexer_files(self):
        if self.mode != 'fix_file':
            return self.qlogs.log("Sorry, but seems you didn't fix any files")

        filename = self.saveFileDialog('fixed_links.txt')

        if filename:
            saved_links = []

            with open(filename, 'w') as file:
                for proces in self.processes_list:
                    for spam_link in proces.links:
                        if spam_link and not spam_link.is_redirect and hash(spam_link) not in saved_links:
                            file.write("{};{};{}\n".format(spam_link.url, spam_link.referer, spam_link.original_count))
                            saved_links.append(hash(spam_link))

            self.qlogs.log("Saved {}".format(filename))

    def save_exception(self, object):
        self.exceptions.append(object)
        site = object['site']
        exception = object['exception']
        # with open('tmp/exceptions.txt', 'w+') as file:
        #     file.write("{}; {}\n".format(site, str(exception)))

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

    def change_upper_limit_state(self):
        self.use_upper_limit = not self.use_upper_limit

    def show_finished_program_info(self):
        redirects = 0
        exceptions = len(self.exceptions)
        processed = 0

        for proces in self.processes_list:
            for link in proces.links:
                if link:
                    if link.is_redirect:
                        redirects += 1
                    else:
                        processed += 1

        self.qlogs.log("Total redirects: {}".format(redirects))
        self.qlogs.log("Total exceptions: {}".format(exceptions))
        self.qlogs.log("Total processed: {}".format(processed))
