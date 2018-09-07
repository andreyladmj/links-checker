import sys
from time import strftime

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QProgressBar, QLabel, QHBoxLayout, QFileDialog, \
    QVBoxLayout, QGroupBox, QGridLayout
from PyQt5.QtCore import pyqtSlot

from utils.file_select import FileSelect
from widgets.link_checker import NewDialog


class App(QWidget, FileSelect):

    def __init__(self):
        super().__init__()
        self.title = 'Check Links'
        self.left = 10
        self.top = 50
        self.width = 1024
        self.height = 840
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # self.button = QPushButton('Choose xlsx report', self)
        # self.button.setToolTip('Parse xlsx file')
        # self.button.move(200, 170)
        # self.button.clicked.connect(self.on_click)
        #
        # self.progressLabel = QLabel('Progress:', self)
        # self.progressBar = QProgressBar(self)
        # self.progressBar.setMaximum(100)
        # self.progressBar.setMinimum(0)
        # self.hboxLayout = QHBoxLayout(self)
        #
        # self.hboxLayout.addWidget(self.progressLabel)
        # self.hboxLayout.addWidget(self.progressBar)
        # self.hboxLayout.addWidget(self.button)
        #
        # # Setting the hBoxLayout as the main layout
        # self.setLayout(self.hboxLayout)
        #
        # self.show()
        self.createGridLayout()

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)

        self.show()

    def createGridLayout(self):
        self.horizontalGroupBox = QGroupBox("Grid")
        layout = QGridLayout()
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 4)

        self.nd = QPushButton('New Window', self)
        self.nd.clicked.connect(self.open_new_dialog)

        layout.addWidget(self.nd,0,0)
        layout.addWidget(QPushButton('2'),0,1)
        layout.addWidget(QPushButton('3'),0,2)
        layout.addWidget(QPushButton('4'),1,0)
        layout.addWidget(QPushButton('5'),1,1)
        layout.addWidget(QPushButton('6'),1,2)
        layout.addWidget(QPushButton('7'),2,0)
        layout.addWidget(QPushButton('8'),2,1)
        layout.addWidget(QPushButton('9'),2,2)

        self.horizontalGroupBox.setLayout(layout)

    def open_new_dialog(self):
        self.nd = NewDialog(self)
        self.nd.show()

    @pyqtSlot()
    def on_click(self):
        self.openFileNameDialog()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
