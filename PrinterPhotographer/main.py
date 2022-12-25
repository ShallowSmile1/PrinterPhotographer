from UI_classes.MainWindow import MainWindow
from PyQt5.QtWidgets import QApplication
import json


if __name__ == "__main__":
    try:
        with open("user_file.json", "r") as load_file:
            data = json.load(load_file)
    except FileNotFoundError:
        with open("dflt_config.json", "r") as load_file:
            data = json.load(load_file)
    app = QApplication([])
    win = MainWindow(data)
    win.show()
    app.exit(app.exec_())
