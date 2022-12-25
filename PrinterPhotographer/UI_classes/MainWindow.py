from PyQt5.QtCore import QThread, Qt
from PyQt5.Qt import QImage, QPixmap
from model.Comport import Comport
from model.Camera import Camera
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
import datetime
import time
import cv2
import os


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
        self.port_num = data["port_num"]
        self.port_command = data["port_command"]
        self.save_dir = data["save_dir"]
        self.delay = data["delay"]
        self.camera_init()
        # self.comport_init()
        self.start_button.clicked.connect(self.com_conn)
        self.settings_btn.clicked.connect(self.open_settings)

    def camera_init(self):
        self.camera = Camera(self.cam_num, self.resolution_w, self.resolution_h)
        self.camera.initialize()
        self.video_thread = VideoThread(main_window=self)
        self.video_thread.start()

    def comport_init(self):
        self.comport = Comport(self.port_num, self.bound_rate, self.byte_size, self.port_command)
        self.comport.initialize()
        self.com_thread = PortThread(
            self.camera,
            self.comport,
            self.save_dir,
            self.delay
        )

    def com_conn(self):
        self.com_thread.start()

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
        self.killthread(self.video_thread)
        self.comport.close_port()
        self.camera.close_camera()
        self.settings = Settings()
        self.settings.setFixedWidth(640)
        self.settings.setFixedHeight(450)
        self.settings.show()
        self.close()

    def killthread(self, thread):
        thread.stop()


