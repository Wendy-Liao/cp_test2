from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread
import subprocess


class Nand(QThread):
    sig_update_ui = pyqtSignal(object)

    def __init__(self, main_ui):
        QThread.__init__(self)
        self.main_ui = main_ui
        self.cmd = 'adb shell ./home/flex/bin/fct1-main.sh  FCT.1.6.1 2 '

    def run(self):
        self.main_ui.under_testing = True
        self.sig_update_ui.emit('Nand test')
        result = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                                  universal_newlines=True)
        (output, err) = result.communicate()
        return_code = result.wait()

        if return_code == 0:
            self.sig_update_ui.emit(output)
            if 'PASS' in output:
                self.main_ui.update_btn_status('NAND', 'Pass')
                self.main_ui.log_to_file('NAND', 'Pass', output)
            else:
                self.main_ui.update_btn_status('NAND', 'Fail')
                self.main_ui.log_to_file('NAND', 'Fail', output)
        else:
            self.sig_update_ui.emit(err)
            self.main_ui.update_btn_status('NAND', 'Fail')
            self.main_ui.log_to_file('NAND', 'Fail', err)
        self.sig_update_ui.emit('Nand end')
        self.main_ui.under_testing = False
