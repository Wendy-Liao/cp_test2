from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread
import subprocess


class ScriptVersion(QThread):
    sig_update_ui = pyqtSignal(object)

    def __init__(self, main_ui):
        QThread.__init__(self)
        self.main_ui = main_ui
        self.cmd = 'adb shell ./home/flex/bin/fct1-main.sh  FCT.1.8.3'

    def run(self):
        self.main_ui.under_testing = True
        self.sig_update_ui.emit('ScriptVersion test')
        result = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                                  universal_newlines=True)
        (output, err) = result.communicate()
        return_code = result.wait()

        if return_code == 0:
            self.sig_update_ui.emit(output)
            if 'BFT_2016-04-07' in output:
                self.main_ui.update_btn_status('ScriptVersion', 'Pass')
                self.main_ui.log_to_file('ScriptVersion', 'Pass', output)
            else:
                self.main_ui.update_btn_status('ScriptVersion', 'Fail')
                self.main_ui.log_to_file('ScriptVersion', 'Fail', output)
        else:
            self.sig_update_ui.emit(err)
            self.main_ui.update_btn_status('ScriptVersion', 'Fail')
            self.main_ui.log_to_file('ScriptVersion', 'Fail', err)
        self.sig_update_ui.emit('ScriptVersion end')
        self.main_ui.under_testing = False