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
import auto_test


class usbBootThread(QThread):
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

        self.check_status_cmd = 'adb devices'
        self.check_status = False
        #self.check_status_action = True
        self.bgtimer = QTimer()
        self.bgtimer.setInterval(1000)
        self.bgtimer.timeout.connect(lambda:self.update_ui(self.check_status))
        self.bgtimer.start()

        self.ui.btnFirmwareversion.clicked.connect(lambda: self.on_btn(self.ui.btnFirmwareversion))
        self.ui.btnNand.clicked.connect(lambda: self.on_btn(self.ui.btnNand))
        self.ui.btnFirmwareversion_2.clicked.connect(lambda: self.on_btn(self.ui.btnFirmwareversion_2))
        self.ui.btnNand_2.clicked.connect(lambda: self.on_btn(self.ui.btnNand_2))
        self.ui.btnFirmwareversion_3.clicked.connect(lambda: self.on_btn(self.ui.btnFirmwareversion_3))
        self.ui.btnNand_3.clicked.connect(lambda: self.on_btn(self.ui.btnNand_3))
        self.ui.autotest.clicked.connect(lambda: self.on_btn(self.ui.autotest))


        self.auto_test_task = auto_test.AutoTest(self)
        self.auto_test_task.sig_update_ui.connect(self.update_message)
        self.firmware_version_task = firmware_version.FirmwareVersion()
        self.task_list.append(self.firmware_version_task)
        self.nand_task = nand.Nand()
        self.task_list.append(self.nand_task)
        self.firmware_version_task2 = firmware_version.FirmwareVersion()
        self.task_list.append(self.firmware_version_task2)
        self.nand_task2 = nand.Nand()
        self.task_list.append(self.nand_task2)
        self.firmware_version_task3 = firmware_version.FirmwareVersion()
        self.task_list.append(self.firmware_version_task3)
        self.nand_task3 = nand.Nand()
        self.task_list.append(self.nand_task3)
        for task in self.task_list:
            task.sig_update_ui.connect(self.update_message)

    def on_btn(self,button):
        running_btn_name = button.text()
        if running_btn_name == 'Auto Test':
            if self.q.empty():
                for task in self.task_list:
                    self.q.put(task)
            self.auto_test_task.start()

        if running_btn_name == 'Firmwareversion':
            self.firmware_version_task.start()

        if running_btn_name == 'NAND':
            self.nand_task.start()

        if running_btn_name == 'Firmwareversion2':
            self.firmware_version_task2.start()

        if running_btn_name == 'NAND2':
            self.nand_task2.start()

        if running_btn_name == 'Firmwareversion3':
            self.firmware_version_task3.start()

        if running_btn_name == 'NAND3':
            self.nand_task3.start()


    def update_message(self, data):
        self.ui.listWidget.addItem(data)


    def update_ui(self, data):
        adb_result = subprocess.Popen(self.check_status_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (output, err) = adb_result.communicate()
        adb_return_code = adb_result.wait()
        check_status = data
        if '2-1' in str(output):
            print('Log: ' + str(adb_return_code) + '; device connected')
            self.enable_button()
            self.check_status = True
        elif not ('2-1' in str(output)):
            print('Log: ' + str(adb_return_code) + '; decice disconnected')
            self.disable_button()
            self.check_status = False


    def enable_button(self):    #set button enable
        self.ui.autotest.setEnabled(True)
        self.ui.btnFirmwareversion.setEnabled(True)
        self.ui.btnNand.setEnabled(True)
        self.ui.btnFirmwareversion_2.setEnabled(True)
        self.ui.btnNand_2.setEnabled(True)
        self.ui.btnFirmwareversion_3.setEnabled(True)
        self.ui.btnNand_3.setEnabled(True)


    def disable_button(self):    #set button disable to click
        self.ui.autotest.setEnabled(False)
        self.ui.btnFirmwareversion.setEnabled(False)
        self.ui.btnNand.setEnabled(False)
        self.ui.btnFirmwareversion_2.setEnabled(False)
        self.ui.btnNand_2.setEnabled(False)
        self.ui.btnFirmwareversion_3.setEnabled(False)
        self.ui.btnNand_3.setEnabled(False)


    def closeEvent(self, event):
        print('Bye')

if __name__ == "__main__":
    import sys

    usbt = usbBootThread()  #for USB boot thread
    usbt.start()

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    time.sleep(1) #wait for adb check
    w.show()
    sys.exit(app.exec_())
