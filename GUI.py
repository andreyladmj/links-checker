import sys
from time import strftime

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QProgressBar, QLabel, QHBoxLayout, QFileDialog
from PyQt5.QtCore import pyqtSlot

from check_links import save_result_report, check_links_in_the_workbook


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Check Links'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 420
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.button = QPushButton('Choose xlsx report', self)
        self.button.setToolTip('Parse xlsx file')
        self.button.move(200, 170)
        self.button.clicked.connect(self.on_click)

        self.progressLabel = QLabel('Progress:', self)
        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(100)
        self.progressBar.setMinimum(0)
        self.hboxLayout = QHBoxLayout(self)

        self.hboxLayout.addWidget(self.progressLabel)
        self.hboxLayout.addWidget(self.progressBar)
        self.hboxLayout.addWidget(self.button)

        # Setting the hBoxLayout as the main layout
        self.setLayout(self.hboxLayout)

        self.show()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            self.thread = ParseXLSX(fileName)
            self.thread.pbar_signal.connect(self.progressBar.setValue)
            self.thread.download_signal.connect(self.saveFileDialog)

            if not self.thread.isRunning():
                self.thread.start()

    def saveFileDialog(self, links):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()",
                                                  strftime("Report-%Y-%m-%d %H-%M-%S.xlsx"),
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print('Save to', fileName)
            save_result_report(fileName, links)

    @pyqtSlot()
    def on_click(self):
        self.openFileNameDialog()


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


def read_file(file):
    with open(file, 'r') as f:
        read_data = f.read()
    return read_data


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
