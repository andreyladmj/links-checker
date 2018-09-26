from time import time

from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, \
    QVBoxLayout, QGroupBox, QGridLayout, QTextEdit, QLabel, QProgressBar, QCheckBox, QLineEdit

from utils.file_select import FileSelect
from utils.qlogger import QLogger


class LCWidget(QWidget, FileSelect):

    def __init__(self, parent, number_of_threads):
        super().__init__()
        self.title = 'Indxer'
        self.left = 10
        self.top = 50
        self.width = 1024
        self.height = 840
        self.parent = parent
        self.processes = number_of_threads

        self.finished = 0

        self.processes_list = []
        self.start_time = 0
        self.qlogs = QLogger(self)

    def _update_status(self):
        if self.start_time:
            self.update_execution_time()

    def update_execution_time(self):
        diff = int(time() - self.start_time)
        days = diff // 86400
        hours = diff // 3600 % 24
        minutes = diff // 60 % 60
        seconds = diff % 60
        self.time_execution_label.setText(
            "Time Execution: {} days, {:02d}:{:02d}:{:02d}".format(days, hours, minutes, seconds))

    def getProcessesUI(self, instanceClass):
        self.processes_list = []
        vbox_layuot = QVBoxLayout()
        self.bars = {}

        for i in range(self.processes):
            hbox_layout = QHBoxLayout()
            parser = instanceClass(number=i, parent=self)

            bar = QProgressBar(self)
            bar.setMaximum(100)
            bar.setMinimum(0)

            self.bars[i] = {
                'label': QLabel('Process: {}'.format(i), self),
                'bar': bar,
            }

            parser.set_bar_updating_bar_func(self.bars[i]['bar'].setValue, self.bars[i]['label'].setText)

            hbox_layout.addWidget(self.bars[i]['label'])
            hbox_layout.addWidget(self.bars[i]['bar'])

            vbox_layuot.addLayout(hbox_layout)
            self.processes_list.append(parser)

        return vbox_layuot

    def is_finished(self):
        return self.finished == self.processes

    def finish(self):
        self.finished += 1

        for process in self.processes_list:
            print('Is process finished', process.number, process.isFinished())

        if self.is_finished():
            self.qlogs.log('Finished!')
            self.update_execution_time()
            self.start_time = 0
            self.show_finished_program_info()

    def show_finished_program_info(self):
        pass

