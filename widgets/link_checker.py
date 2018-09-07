from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QProgressBar, QLabel, QHBoxLayout, QFileDialog, \
    QVBoxLayout, QGroupBox, QGridLayout
from utils.file_select import FileSelect

class NewDialog(QWidget, FileSelect):
    def __init__(self, parent):
        super().__init__()
        self.title = 'Link Checker'
        self.left = 10
        self.top = 50
        self.width = 1024
        self.height = 840
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.horizontalGroupBox = QGroupBox("Grid")

        actions_layout = QGridLayout()
        actions_layout.setColumnStretch(1, 3)
        actions_layout.addWidget(QPushButton('1'),0,0)
        actions_layout.addWidget(QPushButton('2'),0,1)
        actions_layout.addWidget(QPushButton('3'),0,2)

        logs_layout = QGridLayout()
        logs_layout.setColumnStretch(2, 3)

        text = '''
Some logs aowidha wiodhoawi hdoadwh awd awd Some logs aowidha wiodhoawi hdoadwh awd awd Some logs aowidha wiodhoawi hdoadwh awd awd Some logs aowidha wiodhoawi hdoadwh awd awd
Some logs aowidha wiodhoawi hdoadwh awd awd Some logs aowidha wiodhoawi hdoadwh awd awd Some logs aowidha wiodhoawi hdoadwh awd awd Some logs aowidha wiodhoawi hdoadwh awd awd
Some logs aowidha wiodhoawi hdoadwh awd awd Some logs aowidha wiodhoawi hdoadwh awd awd Some logs aowidha wiodhoawi hdoadwh awd awd Some logs aowidha wiodhoawi hdoadwh awd awd
Some logs aowidha wiodhoawi hdoadwh awd awd Some logs aowidha wiodhoawi hdoadwh awd awd Some logs aowidha wiodhoawi hdoadwh awd awd Some logs aowidha wiodhoawi hdoadwh awd awd
        '''

        cols = 3
        rows = 2
        actions_layout.addWidget(QLabel(text, self), 1,0, rows,cols)
        actions_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.horizontalGroupBox.setLayout(actions_layout)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)

        self.show()
