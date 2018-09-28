from PyQt5 import QtCore


class ProccessBarThread(QtCore.QThread):
    pbar_signal = QtCore.pyqtSignal(int)
    plabel_signal = QtCore.pyqtSignal(str)
    log_signal = QtCore.pyqtSignal(str)
    response_signal = QtCore.pyqtSignal(object)
    exception_signal = QtCore.pyqtSignal(object)
    finish_signal = QtCore.pyqtSignal()

    def update_info(self):
        self.pbar_signal.emit(self.processed / self.total * 100)
        self.plabel_signal.emit('Worker: {} (Processed {} of {})'.format(self.number, self.processed, self.total))

    def finish(self):
        self.update_info()
        self.log_signal.emit("Worker: {} Finished!".format(self.number))
        self.finish_signal.emit()

    def set_bar_updating_bar_func(self, bar_fn, label_fn):
        self.pbar_signal.connect(bar_fn)
        self.plabel_signal.connect(label_fn)