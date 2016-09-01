from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread


class AutoTest(QThread):
    sig_update_ui = pyqtSignal(object)

    def __init__(self, main_ui):
        QThread.__init__(self)
        self.main_ui = main_ui
        self.auto_running_task = None

    def run(self):
        self.sig_update_ui.emit('AutoTest')
        self.main_ui.under_auto_testing = True
        while not self.main_ui.q.empty():
            self.sig_update_ui.emit('='*20)
            self.auto_running_task = self.main_ui.q.get()
            self.auto_running_task.start()
            self.auto_running_task.wait()

        self.sig_update_ui.emit('AutoTest end')
        self.main_ui.under_auto_testing = False
