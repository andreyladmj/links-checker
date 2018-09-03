from PyQt5.QtWidgets import QDialog, QProgressBar, QLabel, QHBoxLayout
from PyQt5.QtCore import pyqtSlot, pyqtSignal


class ProgressBar_Dialog(QDialog):
    def __init__(self, on_changed_value):
        super(ProgressBar_Dialog ,self).__init__()
        self.init_ui()
        #self.slider.valueChanged.connect(on_changed_value)

    def init_ui(self):
        # Creating a label
        self.progressLabel = QLabel('Progress Bar:', self)

        # Creating a progress bar and setting the value limits
        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(100)
        self.progressBar.setMinimum(0)

        # Creating a Horizontal Layout to add all the widgets
        self.hboxLayout = QHBoxLayout(self)

        # Adding the widgets
        self.hboxLayout.addWidget(self.progressLabel)
        self.hboxLayout.addWidget(self.progressBar)

        # Setting the hBoxLayout as the main layout
        self.setLayout(self.hboxLayout)
        self.setWindowTitle('Dialog with Progressbar')

        self.show()



import sys
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pb = ProgressBar_Dialog()
    sys.exit(app.exec_())