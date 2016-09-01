from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread
import subprocess


class Wifi(QThread):
    sig_update_ui = pyqtSignal(object)

    def __init__(self, main_ui):
        QThread.__init__(self)
        self.main_ui = main_ui
        self.wifi_setup_cmd = 'adb shell /home/flex/bin/fct1-main.sh FCT.1.2.2'
        self.cmd = 'adb shell /home/flex/bin/fct1-main.sh FCT.1.5.4 antenna_test_1'

    def run(self):
        self.main_ui.under_testing = True
        self.sig_update_ui.emit('Wifi test')

        if self.setup_wifi():
            result = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                                      universal_newlines=True)
            (output, err) = result.communicate()
            return_code = result.wait()

            if return_code == 0:
                self.sig_update_ui.emit(output)
                if 'PASS' in output:
                    self.main_ui.update_btn_status('Wifi', 'Pass')
                    self.main_ui.log_to_file('Wifi' , 'Pass', output)
                else:
                    self.main_ui.update_btn_status('Wifi', 'Fail')
                    self.main_ui.log_to_file('Wifi', 'Fail', output)
            else:
                self.sig_update_ui.emit(err)
                self.main_ui.update_btn_status('Wifi', 'Fail')
                self.main_ui.log_to_file('Wifi', 'Fail', err)
        else:
            self.sig_update_ui.emit('Wifi setup error')
            self.main_ui.update_btn_status('Wifi', 'Fail')
            self.main_ui.log_to_file('Wifi', 'Fail', 'Wifi setup error')
        self.sig_update_ui.emit('Wifi end')
        self.main_ui.under_testing = False

    def setup_wifi(self):

        file_check_result = subprocess.check_output('adb shell ls /tmp/', shell=True, universal_newlines=True)
        if 'wifi' in file_check_result:
            print('Wifi already setup')
            return True
        else:
            wifi_setup_result = subprocess.Popen(self.wifi_setup_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                 shell=True, universal_newlines=True)
            (wifi_setup_output, wifi_setup_err) = wifi_setup_result.communicate()
            if 'Successfully initialized wpa_supplicant' in wifi_setup_output:
                return True
            else:
                self.sig_update_ui.emit(wifi_setup_output)
                return False
