

from PyQt5 import QtCore
from check_links import save_result_report, check_links_in_the_workbook

class ParseXLSX(QtCore.QThread):
    pbar_signal = QtCore.pyqtSignal(int)
    download_signal = QtCore.pyqtSignal(list)

    def __init__(self, fileName):
        super().__init__()
        self.fileName = fileName

    def run(self):
        self.pbar_signal.emit(0)
        links = check_links_in_the_workbook(self.fileName, self.pbar_signal, multi=False)

        self.pbar_signal.emit(100)
        self.download_signal.emit(links)