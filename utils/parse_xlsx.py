import time
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QProgressBar

from check_links import save_result_report, check_links_in_the_workbook

class ParseXLSX(QtCore.QThread):
    pbar_signal = QtCore.pyqtSignal(int)
    download_signal = QtCore.pyqtSignal(list)

    def __init__(self, number, parent):
        super().__init__()
        self.number = number
        self.qlabel = QLabel('Process: {}'.format(self.number), parent)
        self.qbar = QProgressBar(parent)
        self.qbar.setMaximum(100)
        self.qbar.setMinimum(0)
        self.links = []
        self.processed = 0
        self.total = 0
        self.pbar_signal.connect(self.qbar.setValue)

    def set_links(self, links):
        self.pbar_signal.emit(0)
        self.links = list(links)
        self.total = len(self.links)
        self.info()

    def info(self):
        self.qlabel.setText('Worker: {} (Processed {} of {})'.format(self.number, self.processed, self.total))
        self.pbar_signal.emit(self.processed / self.total * 100)

    def run(self):
        for i in range(100):
            self.processed += 1
            self.info()
            time.sleep(1)

        pass
        # self.pbar_signal.emit(0)
        # links = check_links_in_the_workbook(self.fileName, self.pbar_signal, multi=False)
        #
        # self.pbar_signal.emit(100)
        # self.download_signal.emit(links)