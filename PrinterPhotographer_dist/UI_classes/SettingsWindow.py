from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog, QDialogButtonBox
from PyQt5.uic import loadUi
from PyQt5 import QtCore
import json
import cv2


def read_data():
    try:
        with open("user_file.json", "r") as load_file:
            data = json.load(load_file)
    except FileNotFoundError:
        with open("dflt_config.json", "r") as load_file:
            data = json.load(load_file)
    return data


def get_camera_list():
    """
    Test the ports and returns a tuple of str with working ports.
    """
    non_working_ports = []
    dev_port = 0
    working_ports = []
    while len(non_working_ports) < 6:
        camera = cv2.VideoCapture(dev_port)
        if not camera.isOpened():
            non_working_ports.append(dev_port)
        else:
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                working_ports.append(dev_port)
        dev_port += 1
    ports = list(map(str, working_ports))
    return ports


class Settings(QDialog):
    def __init__(self):
        super(Settings, self).__init__()
        loadUi("UI/settings.ui", self)
        self.data = read_data()

        self.parse_data(self.data)

        self.camera_box.addItems(get_camera_list())
        self.resolution.addItems(["640x360", "960x540", "1280x720", "1920x1080", "2560x1440"])

        self.set_str_settings()

        self.choose_dir_btn.clicked.connect(self.choose_dir)

        self.buttonBox.clicked.connect(self.btn_box_click)

    def parse_data(self, data):
        self.camera_d = data["camera"]
        self.resolution_w_d = data["resolution_w"]
        self.resolution_h_d = data["resolution_h"]
        self.port_command_d = data["port_command"]
        self.bound_rate_d = data["bound_rate"]
        self.byte_size_d = data["byte_size"]
        self.port_num_d = data["port_num"]
        self.save_dir_d = data["save_dir"]
        self.delay_d = data["delay"]

    def btn_box_click(self, button):
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.AcceptRole:
            self.ok_act()
        if role == QDialogButtonBox.ResetRole:
            self.reset_act()
        if role == QDialogButtonBox.RejectRole:
            self.cancel_act()

    def cancel_act(self):
        from UI_classes.MainWindow import MainWindow
        window = MainWindow(self.data)
        window.show()
        self.close()

    def ok_act(self):
        str_res = self.resolution.currentText()
        resolution_w, resolution_h = str_res.split(sep="x")
        self.data["camera"] = int(self.camera_box.currentText())
        self.data["resolution_w"] = int(resolution_w)
        self.data["resolution_h"] = int(resolution_h)
        self.data["port_command"] = self.port_command.text()
        self.data["bound_rate"] = int(self.port_boundrate.text())
        self.data["byte_size"] = int(self.port_bytesize.text())
        self.data["port_num"] = self.port_name.text()
        self.data["save_dir"] = self.dir_path.text()
        self.data["delay"] = float(self.delay.text())

        with open('user_file.json', 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

        self.cancel_act()

    def reset_act(self):
        with open("dflt_config.json", "r") as load_file:
            data = json.load(load_file)
        self.parse_data(data)
        self.set_str_settings()

    def set_str_settings(self):
        resolution = str(self.resolution_w_d) + "x" + str(self.resolution_h_d)
        index = self.resolution.findText(resolution, QtCore.Qt.MatchFixedString)
        self.resolution.setCurrentIndex(index)
        self.port_command.setText(self.port_command_d)
        self.port_boundrate.setText(str(self.bound_rate_d))
        self.port_bytesize.setText(str(self.byte_size_d))
        self.port_name.setText(self.port_num_d)
        self.dir_path.setText(self.save_dir_d)
        self.delay.setText(str(self.delay_d))
        index = self.camera_box.findText(str(self.camera_d), QtCore.Qt.MatchFixedString)
        self.camera_box.setCurrentIndex(index)

    def choose_dir(self):
        res = QFileDialog.getExistingDirectory(self, "Choose directory", ".")
        self.dir_path.setText(res)
