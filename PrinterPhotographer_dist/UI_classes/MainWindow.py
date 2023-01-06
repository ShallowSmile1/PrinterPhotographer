from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread, Qt
from PyQt5.Qt import QImage, QPixmap
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from serial import SerialException
import datetime
import time
import cv2
import os
from model.Comport import Comport
from model.Camera import Camera


class VideoThread(QThread):
    def __init__(self, main_window, parent=None):
        super(VideoThread, self).__init__(parent)
        self.thredactive = True
        self.main_win = main_window

    def run(self):
        while self.thredactive:
            self.main_win.update_image()

    def stop(self):
        self.thredactive = False
        self.wait()


class PortThread(QThread):
    def __init__(self, camera, comport, save_dir, delay, parent=None):
        super(PortThread, self).__init__(parent)
        self.thredactive = True
        self.camera = camera
        self.port = comport
        self.pic_num = 0
        self.path = save_dir
        self.delay = delay

    def run(self):
        cur_path = self.path + "\\" + datetime.datetime.now().strftime("%I %M%p_%B_%d_%Y")
        os.makedirs(cur_path)
        while self.thredactive:
            if self.port.check_command():
                time.sleep(self.delay)
                cv2.imwrite(cur_path + '\\' + str(self.pic_num) + ".jpg", self.camera.get_frame())
                self.pic_num += 1

    def stop(self):
        self.thredactive = False
        self.wait()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, data):
        super(MainWindow, self).__init__()
        loadUi("UI/main.ui", self)
        self.camera = None
        self.video_thread = None
        self.comport = None
        self.com_thread = None
        self.cam_num = data["camera"]
        self.resolution_w = data["resolution_w"]
        self.resolution_h = data["resolution_h"]
        self.bound_rate = data["bound_rate"]
        self.byte_size = data["byte_size"]
        self.port_command = data["port_command"]
        self.port_num = data["port_num"]
        self.save_dir = data["save_dir"]
        self.delay = data["delay"]
        self.camera_init()
        self.comport_init()
        self.start_button.clicked.connect(self.com_conn)
        self.settings_btn.clicked.connect(self.open_settings)
        self.stop_btn.clicked.connect(self.stop_com_thread)
        self.button_stilesheet(self.stop_btn, False)

    def stop_com_thread(self):
        if self.com_thread:
            self.killthread(self.com_thread)
            self.button_stilesheet(self.start_button, True)
            self.button_stilesheet(self.stop_btn, False)

    def camera_init(self):
        self.camera = Camera(self.cam_num, self.resolution_w, self.resolution_h)
        try:
            self.camera.initialize()
            self.video_thread = VideoThread(main_window=self)
            self.video_thread.start()
        except FileNotFoundError:
            QMessageBox.critical(self, "Error",
                                 f"Camera connection error.\nTry to change camera configs to correct ones or check camera connection.",
                                 QMessageBox.Ok)
            self.button_stilesheet(self.start_button, False)


    def comport_init(self):
        self.comport = Comport(self.port_num, self.bound_rate, self.byte_size, self.port_command)
        try :
            self.comport.initialize()
            self.com_thread = PortThread(
                self.camera,
                self.comport,
                self.save_dir,
                self.delay
            )
        except FileNotFoundError:
            QMessageBox.critical(self, "Error",
                                 f"No port \"{self.port_num}\", try change port at settings.",
                                 QMessageBox.Ok)
            self.button_stilesheet(self.start_button, False)
        except SerialException:
            QMessageBox.critical(self, "Error",
                                 f"Cannot create connection to port \"{self.port_num}\", try change port at settings.",
                                 QMessageBox.Ok)
            self.button_stilesheet(self.start_button, False)
        except OSError:
            QMessageBox.critical(self, "Error",
                                 f"Port \"{self.port_num}\" is unavailable, try change port at settings.",
                                 QMessageBox.Ok)
            self.button_stilesheet(self.start_button, False)

    def com_conn(self):
        self.com_thread.start()
        self.start_button.setEnabled(False)
        self.button_stilesheet(self.start_button, False)
        self.button_stilesheet(self.stop_btn, True)

    def update_image(self):
        frame = self.camera.get_frame()
        rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgbImage.shape
        bytesPerLine = ch * w
        convert_to_qt_format = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
        p = convert_to_qt_format.scaled(1400, 900, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.video_widget.setPixmap(QPixmap.fromImage(p))

    def open_settings(self):
        from UI_classes.SettingsWindow import Settings
        if self.video_thread:
            self.killthread(self.video_thread)
        if self.com_thread:
            self.killthread(self.com_thread)
        if self.comport.connect:
            self.comport.close_port()
        if self.camera.cap:
            self.camera.close_camera()
        self.settings = Settings()
        self.settings.setFixedWidth(640)
        self.settings.setFixedHeight(450)
        self.settings.show()
        self.close()

    def killthread(self, thread):
        thread.stop()

    def button_stilesheet(self, btn, active):
        if active:
            btn.setStyleSheet("background-color: rgb(173, 173, 173); font-size: 18pt; color:rgb(54, 54, 54)")
        else:
            btn.setStyleSheet("background-color: rgb(143, 143, 143); font-size: 18pt; color:rgb(54, 54, 54)")
        btn.setEnabled(active)
