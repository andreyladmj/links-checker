from collections import Counter
from os import cpu_count
from random import shuffle

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, \
    QVBoxLayout, QGroupBox, QGridLayout, QTextEdit

from utils.file_select import FileSelect
from utils.indexer_site_checker import IndexerSiteChecker
from utils.utils import iterate_by_batch, make_xlsx_file


class SpamLink:
    __slots__ = ('url', 'referer', 'count')

    def __init__(self, url, referer, count):
        self.url = url
        self.referer = referer
        self.count = count


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

        # self.fix_indexer_files_button = QPushButton('Fix Indexer Files', self)
        # self.fix_indexer_files_button.clicked.connect(self.select_files_for_indexer_fix)

        actions_layout = QGridLayout()
        actions_layout.addWidget(self.select_xlsx_button, 0, 0)
        actions_layout.addWidget(self.start_process_button, 0, 1)
        actions_layout.addWidget(self.export_xlsx_report_button, 0, 2)
        actions_layout.addWidget(self.export_xlsx_exceptions_report_button, 0, 3)
        actions_layout.addWidget(self.export_xlsx_redirects_report_button, 0, 4)
        # actions_layout.addWidget(self.fix_indexer_files_button, 0, 5)
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

        self.qlabel_logs = QTextEdit("", self)
        self.qlabel_logs.setLineWrapMode(QTextEdit.NoWrap)
        self.qlabel_logs.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        windowLayout.addLayout(vbox_layuot)
        windowLayout.addWidget(filterGroupBox)
        windowLayout.addWidget(self.qlabel_logs)
        self.setLayout(windowLayout)

        self.show()

    def log(self, string):
        self.logs.append(string)
        self.qlabel_logs.setText("\n".join(self.logs))
        self.qlabel_logs.verticalScrollBar().setValue(self.qlabel_logs.verticalScrollBar().maximum())

    def set_logs(self, arr):
        self.qlabel_logs.setText("\n".join(arr))
        # self.qlabel_logs.moveCursor(QTextCursor.End)
        self.qlabel_logs.verticalScrollBar().setValue(self.qlabel_logs.verticalScrollBar().maximum())

    def select_xlsx_dialog(self):
        files = self.openFileNamesDialog()
        if files:
            self.log("Selected files {}".format(', '.join(files)))
            self.files = files

    def show_all_logs(self):
        self.set_logs(self.logs)

    def show_all_redirected(self):
        redirected = []
        for response in self.sites_responses:
            if response.status_code == 301:
                redirected.append("{} redirected to {}\n".format(response.url, response.headers.get('Location')))

        self.set_logs(redirected)

    def show_all_exceptions(self):
        exceptions = ["{}: {}".format(exception['site'], exception['exception']) for exception in self.exceptions]
        self.set_logs(exceptions)

    def parse_xlsx_files(self):
        links = []

        if not len(self.files):
            return self.log('Please select file')
        else:
            self.log("Starting parse files...")

        for file in self.files:
            links += self.get_links(file)

        self.log("Total links: {}".format(len(links)))

        batch_size = len(links) // self.processes + 1
        self.log('Batch Size: {}'.format(batch_size))

        batches = iterate_by_batch(links, batch_size, None)

        for process, batch in zip(self.processes_list, batches):
            process.set_links(batch)
            process.start()

    def get_links(self, file, for_checking=False):
        urls = []
        with open(file, 'r') as file:
            for line in file.readlines():
                site, referer, count = line.split(';')
                count = int(count.rstrip())

                if for_checking:
                    urls += [(site, referer)]
                else:
                    urls += [(site, referer)] * count

        shuffle(urls)
        return urls

    def export_xlsx_report(self):
        cnt = Counter()
        responses = self.sites_responses

        for response in responses:
            cnt[response.url] += 1

        make_xlsx_file('report_sa.xlsx', head=['Site', 'Count'], body=cnt.items())

    def export_xlsx_exceptions_report(self):
        report = []
        for exception in self.exceptions:
            report.append([exception['site'], str(exception['exception'])])

        make_xlsx_file('report_exceptions.xlsx', head=['Site', 'Exception'], body=report)

    def export_xlsx_redirects_report(self):
        report = []
        responses = self.sites_responses
        for response in responses:
            if response.status_code == 301:
                report.append([response.url, response.headers.get('Location')])

        make_xlsx_file('report_redirect.xlsx', head=['Site', 'Redirect To'], body=report)

    def select_files_for_indexer_fix(self):
        file = self.openFileNameDialog()
        if file:
            self.log("Trying to fix selected file {}".format(file))
            self.fix_indexer_files(file)

    def finish(self):
        self.log('Finished!')
