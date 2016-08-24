from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread
import subprocess


class FirmwareVersion(QThread):
    sig_update_ui = pyqtSignal(object)

    def __init__(self, main_ui):
        QThread.__init__(self)
        self.main_ui = main_ui
        self.cmd = 'adb shell ./home/flex/bin/fct1-main.sh  FCT.1.8.2'

    def run(self):
        self.sig_update_ui.emit('FirmwareVersion test')
        self.main_ui.under_testing = True
        result = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (output, err) = result.communicate()
        return_code = result.wait()
        if return_code == 0:
            self.sig_update_ui.emit(str(output, encoding='UTF-8'))
        else:
            self.sig_update_ui.emit(str(err, encoding='UTF-8'))
        self.sig_update_ui.emit('FirmwareVersion end')
        self.main_ui.under_testing = False
