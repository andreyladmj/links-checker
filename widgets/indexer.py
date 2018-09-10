from multiprocessing import Queue
from os import cpu_count
from random import shuffle

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QProgressBar, QLabel, QHBoxLayout, QFileDialog, \
    QVBoxLayout, QGroupBox, QGridLayout, QScrollBar, QTextEdit
from openpyxl import load_workbook

from utils.file_select import FileSelect
from utils.parse_xlsx import ParseXLSX
from utils.utils import iterate_by_batch


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
        self.queue = Queue()
        self.logs = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.horizontalGroupBox = QGroupBox("Grid")

        self.select_xlsx = QPushButton('Select XLSX')
        self.select_xlsx.clicked.connect(self.select_xlsx_dialog)

        # vbox_layout = QHBoxLayout()
        vbox_layuot = QVBoxLayout()

        for i in range(self.processes):
            hbox_layout = QHBoxLayout()
            parser = ParseXLSX(number=i, parent=self)

            hbox_layout.addWidget(parser.qlabel)
            hbox_layout.addWidget(parser.qbar)
            vbox_layuot.addLayout(hbox_layout)
            self.processes_list.append(parser)


        self.qlabel_logs = QTextEdit("", self)
        self.qlabel_logs.setLineWrapMode(QTextEdit.NoWrap)
        self.qlabel_logs.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # self.horizontalGroupBox.setLayout(actions_layout)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        windowLayout.addWidget(self.select_xlsx)
        windowLayout.addLayout(vbox_layuot)
        windowLayout.addWidget(self.qlabel_logs)
        self.setLayout(windowLayout)

        self.show()

    def log(self, string):
        self.logs.append(string)
        self.qlabel_logs.setText("\n".join(self.logs))

    def select_xlsx_dialog(self):
        file = self.openFileNameDialog()
        if file:
            self.log("Selected file {}".format(file))
            self.parse_xlsx_file(file)

    def parse_xlsx_file(self, file):
        links = self.get_links(file)
        self.log("Total links: {}".format(len(links)))

        return

        links = list(ws.iter_rows())

        batch_size = len(links) // self.processes + 1
        self.log('Total Links Count: {}, Batch Size: {}'.format(len(links), batch_size))

        batches = iterate_by_batch(links, batch_size, None)

        for process, batch in zip(self.processes_list, batches):
            process.set_links(batch)
            process.set_queue(self.queue)
            process.start()

    def get_links(self, file):
        urls = []
        with open(file, 'r') as file:
            for line in file.readlines():
                domain, site, count = line.split(';')
                count = int(count.rstrip())

                urls += [(domain, site)] * count

        shuffle(urls)
        return urls
