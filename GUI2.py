import sys
from time import strftime
from os import cpu_count

from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QProgressBar, QLabel, QHBoxLayout, QFileDialog, \
    QVBoxLayout, QGroupBox, QGridLayout, QLineEdit
from PyQt5.QtCore import pyqtSlot

from utils.file_select import FileSelect
from widgets.indexer import Indexer
from widgets.link_checker import CheckAcceptors
from widgets.wp_comments import WPComments


class App(QWidget, FileSelect):

    def __init__(self):
        super().__init__()
        self.title = 'Check Links'
        self.left = 10
        self.top = 50
        self.width = 512
        self.height = 320
        self.number_of_threads = cpu_count()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        layout = self.createGridLayout()
        self.setLayout(layout)

        self.show()

    def createGridLayout(self):
        layout = QGridLayout()
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 4)

        self.check_acceptors = QPushButton('Check Acceptors', self)
        self.check_acceptors.clicked.connect(self.open_new_dialog)

        self.indexer = QPushButton('Run Indexer', self)
        self.indexer.clicked.connect(self.open_indexer_window)

        self.wp_comments_button = QPushButton('WP Comments', self)
        self.wp_comments_button.clicked.connect(self.open_wp_comments_window)

        layout.addWidget(self.check_acceptors,0,0)
        layout.addWidget(self.indexer,0,1)
        layout.addWidget(self.wp_comments_button,0,2)

        hbox_layout = QVBoxLayout()
        hbox_layout.addWidget(self.getSettingsUI())
        hbox_layout.addLayout(layout)
        return hbox_layout

    def open_new_dialog(self):
        self.check_acceptors = CheckAcceptors(self, self.number_of_threads)
        self.check_acceptors.show()

    def open_indexer_window(self):
        self.indexer_window = Indexer(self, self.number_of_threads)
        self.indexer_window.show()

    def open_wp_comments_window(self):
        self.wp_comments_window = WPComments(self)
        self.wp_comments_window.show()

    @pyqtSlot()
    def on_click(self):
        self.openFileNameDialog()

    def getSettingsUI(self):
        settingsGroupBox = QGroupBox("Settings")
        settingsGridLayout = QGridLayout()

        self.settings_threads = QLineEdit()
        self.settings_threads.setValidator(QIntValidator(0, 20))
        self.settings_threads.setText(str(self.number_of_threads))
        self.settings_threads.setMaximumWidth(50)

        self.settings_threads_apply_button = QPushButton('Set Number of Processes')
        self.settings_threads_apply_button.clicked.connect(self.settings_threads_apply)

        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(QLabel('Number of processes', self))
        hbox_layout.addWidget(self.settings_threads)
        hbox_layout.addWidget(self.settings_threads_apply_button)

        settingsGridLayout.addLayout(hbox_layout, 1, 0)
        settingsGroupBox.setLayout(settingsGridLayout)
        settingsGroupBox.setMaximumHeight(100)
        return settingsGroupBox

    def settings_threads_apply(self):
        self.number_of_threads = int(self.settings_threads.text())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
