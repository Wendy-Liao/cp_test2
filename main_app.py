# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QThread
from gui import Ui_MainWindow
from queue import Queue
import subprocess
import os
import time
import firmware_version
import nand
import wifi
import script_version
import auto_test


class UsbBootThread(QThread):
    def __init__(self):
        QThread.__init__(self)

    def run(self):
        try:
            usbboot_version = 'bg2cdp_usbboot_host_2016-06-05'
            if os.name == 'nt':  # Windows
                cmd = [usbboot_version + '\\bin\\run_a0.bat']
                subprocess.check_output(cmd, shell=True).decode("utf-8")
            elif os.name == 'posix':  # Ubuntu
                cmd = ['sudo ./' + usbboot_version + '/build/out/usb_boot 1286 8174 ./' + usbboot_version + '/bin/images_a0/ 8141 "putty telnet://127.0.0.1:8141"']
                subprocess.check_output(cmd, shell=True).decode("utf-8")
            else:
                print('[CP] Please comfirm your operating system!(Windows/Ubuntu?)')
        except subprocess.CalledProcessError as e:
            print('[CP] Please check the usbboot host folder!')


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.q = Queue()
        self.task_list = []
        self.btn_dict = {'Auto Test': self.ui.autotest,
                         'FirmwareVersion': self.ui.btnFirmwareVersion,
                         'NAND': self.ui.btnNand,
                         'Wifi': self.ui.btnWifi,
                         'ScriptVersion': self.ui.btnScriptVersion,
                         'Firmwareversion3': self.ui.btnFirmwareversion_3,
                         'NAND3': self.ui.btnNand_3
                         }

        self.check_status_cmd = 'adb devices'
        self.check_status = False
        self.under_auto_testing = False        # switch; lock buttons while under autotesting
        self.under_testing = False    # switch; lock buttons while under testing
        self.bgtimer = QTimer()
        self.bgtimer.setInterval(1000)
        self.bgtimer.timeout.connect(self.update_ui)
        self.bgtimer.start()

        self.ui.lineEdit.returnPressed.connect(self.ui.autotest.click)
        for btn_object in self.btn_dict.values():
            btn_object.clicked.connect(self.on_btn)

        self.auto_test_task = auto_test.AutoTest(self)
        self.auto_test_task.sig_update_ui.connect(self.update_message)
        self.firmware_version_task = firmware_version.FirmwareVersion(self)
        self.task_list.append(self.firmware_version_task)
        self.nand_task = nand.Nand(self)
        self.task_list.append(self.nand_task)
        self.wif_task = wifi.Wifi(self)
        self.task_list.append(self.wif_task)
        self.script_version_task = script_version.ScriptVersion(self)
        self.task_list.append(self.script_version_task)
        self.firmware_version_task3 = firmware_version.FirmwareVersion(self)
        self.task_list.append(self.firmware_version_task3)
        self.nand_task3 = nand.Nand(self)
        self.task_list.append(self.nand_task3)
        for task in self.task_list:
            task.sig_update_ui.connect(self.update_message)

    def on_btn(self):
        running_btn_name = self.sender().text()
        if running_btn_name == 'Auto Test':
            if self.q.empty():
                for task in self.task_list:
                    self.q.put(task)
            self.auto_test_task.start()

        if running_btn_name == 'FirmwareVersion':
            self.firmware_version_task.start()

        if running_btn_name == 'NAND':
            self.nand_task.start()

        if running_btn_name == 'Wifi':
            self.wif_task.start()

        if running_btn_name == 'ScriptVersion':
            self.script_version_task.start()

        if running_btn_name == 'Firmwareversion3':
            self.firmware_version_task3.start()

        if running_btn_name == 'NAND3':
            self.nand_task3.start()

    def update_message(self, data):
        self.ui.listWidget.scrollToBottom()
        self.ui.listWidget.addItem(data)

    def update_ui(self):
        adb_result = subprocess.Popen(self.check_status_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                                      universal_newlines=True)
        (output, err) = adb_result.communicate()
        adb_return_code = adb_result.wait()
        self.ui.lineEdit.setFocus()
        if '3-4' in output:
            print('Log: %d' % adb_return_code + '; device connected')
            self.check_status = True
            if self.under_auto_testing or self.under_testing:
                self.disable_button()
                self.ui.lineEdit.setEnabled(False)
            else:
                self.enable_button()
                self.ui.lineEdit.setEnabled(True)
        else:
            print('Log: %d' % adb_return_code + '; device disconnected')
            if self.q.empty():
                self.ui.lineEdit.clear()
                for btn in self.btn_dict.values():
                    btn.setStyleSheet("background-color: rgb(242, 241, 240)")
            self.disable_button()
            self.check_status = False

    def update_btn_status(self, item_name, status):
        running_btn = self.btn_dict.get(item_name)
        if status == 'Pass':
            running_btn.setStyleSheet("background-color: rgb(0, 255, 0)")
        elif status == 'Fail':
            running_btn.setStyleSheet("background-color: rgb(255, 0, 0)")

    def enable_button(self):    # set button enable
        for btn in self.btn_dict.values():
            btn.setEnabled(True)

    def disable_button(self):    # set button disable to click
        for btn in self.btn_dict.values():
            btn.setEnabled(False)

    def log_to_file(self, item_name, status, description):
        serial_number = self.ui.lineEdit.text()
        timestamp = time.strftime("%Y%m%d%H%M", time.localtime())
        log_summary = './log/' + serial_number + '/' + timestamp + '.log'
        status_summary = './log/' + serial_number + '/status_summary.log'
        os.makedirs(os.path.dirname(log_summary), exist_ok=True)
        os.makedirs(os.path.dirname(status_summary), exist_ok=True)
        with open(log_summary, 'a') as f:
            f.write('name :' + item_name + '\n' + description + '\n')
            f.close()

        with open(status_summary, 'a') as f1:
            f1.write('name :' + item_name + '\n' + 'status :' + status + '\n')
            f1.close()

    def closeEvent(self, event):
        print('Bye')

if __name__ == "__main__":
    import sys

    #usbt = UsbBootThread()  #for USB boot thread
    #usbt.start()

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    time.sleep(1) #wait for adb check
    w.show()
    sys.exit(app.exec_())
