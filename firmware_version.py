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
        self.main_ui.under_testing = True
        self.sig_update_ui.emit('FirmwareVersion test')
        result = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                                  universal_newlines=True)
        (output, err) = result.communicate()
        return_code = result.wait()
        if return_code == 0:
            self.sig_update_ui.emit(output)
            if 'UNKNOWN' in output:
                self.main_ui.update_btn_status('FirmwareVersion', 'Pass')
                self.main_ui.log_to_file('FirmwareVersion', 'Pass', output)
            else:
                self.main_ui.update_btn_status('FirmwareVersion', 'Fail')
                self.main_ui.log_to_file('FirmwareVersion', 'Fail', output)
        else:
            self.sig_update_ui.emit(err)
            self.main_ui.update_btn_status('FirmwareVersion', 'Fail')
            self.main_ui.log_to_file('FirmwareVersion', 'Fail', err)
        self.sig_update_ui.emit('FirmwareVersion end')
        self.main_ui.under_testing = False
