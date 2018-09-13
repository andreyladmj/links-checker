
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTextEdit


class QLogger(QTextEdit):
    def __init__(self, parent):
        super().__init__("", parent)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.logs = []

    def log(self, string):
        self.logs.append(string)
        self.setText("\n".join(self.logs))
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def set_logs(self, arr):
        self.setText("\n".join(arr))
        # self.qlabel_logs.moveCursor(QTextCursor.End)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())