from time import strftime

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QProgressBar, QLabel, QHBoxLayout, QFileDialog

class FileSelect:
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py)", options=options)
        return fileName
        # if fileName:
        #     self.thread = ParseXLSX(fileName)
        #     self.thread.pbar_signal.connect(self.progressBar.setValue)
        #     self.thread.download_signal.connect(self.saveFileDialog)
        #
        #     if not self.thread.isRunning():
        #         self.thread.start()

    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
                                                "All Files (*);;Python Files (*.py)", options=options)
        if files:
            return files

    def saveFileDialog(self, links):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()",
                                                  strftime("Report-%Y-%m-%d %H-%M-%S.xlsx"),
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        return fileName
        # if fileName:
        #     print('Save to', fileName)
        #     save_result_report(fileName, links)