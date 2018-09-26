from multiprocessing import Queue
from os import cpu_count

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QProgressBar, QLabel, QHBoxLayout, QFileDialog, \
    QVBoxLayout, QGroupBox, QGridLayout, QScrollBar, QTextEdit
from openpyxl import load_workbook

from utils.file_select import FileSelect
from utils.parse_xlsx import ParseXLSX
from utils.qlogger import QLogger
from utils.utils import iterate_by_batch
from widgets.lcwidget import LCWidget


class CheckAcceptors(LCWidget):

    def __init__(self, parent, number_of_threads):
        super().__init__(parent, number_of_threads)
        self.title = 'Acceptor Checker'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.horizontalGroupBox = QGroupBox("Checker")

        self.select_xlsx = QPushButton('Select XLSX')
        self.select_xlsx.clicked.connect(self.select_xlsx_dialog)

        self.export_xlsx_button = QPushButton('Export XLSX Report')
        self.export_xlsx_button.clicked.connect(self.export_xlsx)

        actions_layout = QGridLayout()
        actions_layout.setColumnStretch(1, 3)
        actions_layout.addWidget(self.select_xlsx,0,0)
        actions_layout.addWidget(QPushButton('Export Logs'),0,1)
        actions_layout.addWidget(self.export_xlsx_button,0,2)

        vbox_layuot = self.getProcessesUI(ParseXLSX)

        actions_layout.addLayout(vbox_layuot, 1, 0, 1, 2)

        self.horizontalGroupBox.setLayout(actions_layout)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        windowLayout.addWidget(self.qlogs)
        self.setLayout(windowLayout)

        self.show()

    def select_xlsx_dialog(self):
        file = self.openFileNameDialog()
        if file:
            self.qlogs.log("Selected file {}".format(file))
            self.parse_xlsx_file(file)

    def parse_xlsx_file(self, file):
        wb = load_workbook(file)
        ws = wb.active

        links = list(ws.iter_rows())

        batch_size = len(links) // self.processes + 1
        self.qlogs.log('Total Links Count: {}, Batch Size: {}'.format(len(links), batch_size))

        batches = iterate_by_batch(links, batch_size, None)

        for process, batch in zip(self.processes_list, batches):
            process.set_links(batch)
            process.start()

    def show_finished_program_info(self):
        self.qlogs.log('Finished!')

    def export_xlsx(self):
        pass