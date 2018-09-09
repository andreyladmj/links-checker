from os import cpu_count

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QProgressBar, QLabel, QHBoxLayout, QFileDialog, \
    QVBoxLayout, QGroupBox, QGridLayout
from openpyxl import load_workbook

from utils.file_select import FileSelect
from utils.parse_xlsx import ParseXLSX
from utils.utils import iterate_by_batch


class CheckAcceptors(QWidget, FileSelect):
    def __init__(self, parent):
        super().__init__()
        self.title = 'Acceptor Checker'
        self.left = 10
        self.top = 50
        self.width = 1024
        self.height = 840
        self.parent = parent
        self.processes = cpu_count()
        self.processes_list = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.horizontalGroupBox = QGroupBox("Grid")

        self.select_xlsx = QPushButton('Select XLSX')
        self.select_xlsx.clicked.connect(self.select_xlsx_dialog)

        actions_layout = QGridLayout()
        actions_layout.setColumnStretch(1, 3)
        actions_layout.addWidget(self.select_xlsx,0,0)
        actions_layout.addWidget(QPushButton('Export Logs'),0,1)
        actions_layout.addWidget(QPushButton('3'),0,2)

        vbox_layuot = QVBoxLayout()

        for i in range(self.processes):
            hbox_layout = QHBoxLayout()
            parser = ParseXLSX(number=i, parent=self)

            hbox_layout.addWidget(parser.qlabel)
            hbox_layout.addWidget(parser.qbar)
            vbox_layuot.addLayout(hbox_layout)
            self.processes_list.append(parser)

        actions_layout.addLayout(vbox_layuot, 1, 0, 1, 2)

        self.logs = ""

        cols = 3
        rows = 2
        self.qlabel_logs = QLabel(self.logs, self)
        actions_layout.addWidget(self.qlabel_logs, 2,0, rows,cols)
        actions_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.horizontalGroupBox.setLayout(actions_layout)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)

        self.show()

    def log(self, string):
        self.logs += string
        self.logs += "\n"
        self.qlabel_logs.setText(self.logs)

    def select_xlsx_dialog(self):
        file = self.openFileNameDialog()
        if file:
            self.log("Selected file {}".format(file))
            self.parse_xlsx_file(file)
        else:
            print('No file')

    def parse_xlsx_file(self, file):
        wb = load_workbook(file)
        ws = wb.active

        links = list(ws.iter_rows())

        batch_size = len(links) // self.processes + 1
        self.log('Total Links Count: {}, Batch Size: {}'.format(len(links), batch_size))

        batches = iterate_by_batch(links, batch_size, None)

        for process, batch in zip(self.processes_list, batches):
            process.set_links(batch)
