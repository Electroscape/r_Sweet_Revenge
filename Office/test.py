# @author Martin Pek (martin.pek@web.de)

'''
 * password via cfg


'''

import sys

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QStackedWidget, QDialog, QFrame, QLineEdit, QHBoxLayout
)

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from time import sleep
from pathlib import Path
import json

import argparse

argparser = argparse.ArgumentParser(
    description='Christines Office')

argparser.add_argument(
    '-c',
    '--city',
    default='s',
    help='name of the city: [hh / s]')



root_path = Path(__file__).parent
args = argparser.parse_args()
city = args.city
img_folder_locale = root_path.joinpath(f"img/{city}")
img_folder_root = root_path.joinpath(f"img")
if not img_folder_locale.exists():
    print(img_folder_locale)
    exit(f"invalid location argument, no image folder found {city}")

def get_img(name, ignore_locale=False):
    if ignore_locale:
        return  str(img_folder_root.joinpath(name))
    return str(img_folder_locale.joinpath(name))

def get_localized_cfg_entry(cfg, key, lang, default):
    return cfg.get(key, {}).get(lang, default)



class PageOne(QWidget):
    def __init__(self, switch_callback):
        super().__init__()
        self.switch_callback = switch_callback

        screen_file = get_img("startscreen.png")
        print(f"screen exists {Path(screen_file).exists()} {screen_file}")
        self.bg_label = QLabel(self)
        self.bg_pixmap = QPixmap(screen_file)

        self.bg_label.setScaledContents(True)
        self.bg_label.lower()  # Ensure it's behind other widgets

        # Create the button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(300)  # ← Reduce gap between buttons
        button_layout.setContentsMargins(0, 0, 0, 0)  # ← Remove extra padding around layout
        button_layout.setAlignment(Qt.AlignCenter)  # ← Make sure buttons stay centered
        button_size = 200

        btn_deu = QPushButton()
        btn_deu.setIcon(QtGui.QIcon(get_img("deu.png", True)))
        btn_deu.setIconSize(QtCore.QSize(button_size - 20, button_size - 20))
        btn_deu.setFixedSize(button_size, button_size)
        btn_deu.setStyleSheet("""
            QPushButton {
                border: 4px solid gray;
                border-radius: %dpx;
                background-color: white;
            }
            QPushButton:pressed {
                background-color: #f0f0f0;
            }
        """ % (button_size // 2))

        btn_eng = QPushButton()
        btn_eng.setIcon(QtGui.QIcon(get_img("eng.png", True)))
        btn_eng.setIconSize(QtCore.QSize(button_size - 20, button_size - 20))
        btn_eng.setFixedSize(button_size, button_size)
        btn_eng.setStyleSheet("""
            QPushButton {
                border: 4px solid gray;
                border-radius: %dpx;
                background-color: white;
            }
            QPushButton:pressed {
                background-color: #f0f0f0;
            }
        """ % (button_size // 2))

        btn_deu.clicked.connect(lambda: self.switch_callback("deu"))
        btn_eng.clicked.connect(lambda: self.switch_callback("eng"))

        button_layout.addWidget(btn_deu)
        button_layout.addWidget(btn_eng)

        # Centered layout
        outer_layout = QVBoxLayout()
        # outer_layout.setAlignment(Qt.AlignCenter)
        outer_layout = QVBoxLayout()
        outer_layout.addStretch(3)  # Push content down

        outer_layout.addLayout(button_layout)

        outer_layout.addStretch(1)  # Optional: push from below if you want center-ish control
        self.setLayout(outer_layout)


    def resizeEvent(self, event):
        if not self.bg_pixmap.isNull():
            # Scale while preserving aspect ratio, crop to fill
            scaled = self.bg_pixmap.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            self.bg_label.setPixmap(scaled)
            self.bg_label.resize(self.size())
        super().resizeEvent(event)




class PageTwo(QWidget):
    def __init__(self, switch_callback, lang, config):
        super().__init__()
        self.language = lang
        self.config = config
        print(f"going page 2 with {self.language}")
        self.setStyleSheet("background-color: white;")

        self.correct_password = config.get("password")  # ✅ Define your expected password
        self.switch_callback = switch_callback

        self.dialog = QDialog(self)
        self.dialog.setWindowFlags(Qt.Widget)
        self.setupUi(self.dialog)
        self.loginBtn.clicked.connect(self.try_login)  # ✅ Changed to use try_login
        self.center_dialog()

        layout = QVBoxLayout(self)
        layout.addWidget(self.dialog)
        self.setLayout(layout)


    def center_dialog(self):
        # Create layout to center dialog
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignCenter)

        outer_layout.addStretch()
        inner_layout = QHBoxLayout()
        inner_layout.addStretch()
        inner_layout.addWidget(self.dialog)
        inner_layout.addStretch()
        outer_layout.addLayout(inner_layout)
        outer_layout.addStretch()

        self.setLayout(outer_layout)

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(500, 340)

        self.setStyleSheet("background-color: white;")
        self.loginBtn = QPushButton(Dialog)
        self.loginBtn.setGeometry(QtCore.QRect(200, 220, 89, 25))
        self.loginBtn.setObjectName("loginBtn")

        self.hintButton = QPushButton(Dialog)
        self.hintButton.setGeometry(QtCore.QRect(300, 220, 151, 25))
        self.hintButton.setObjectName("hintButton")
        self.hintButton.clicked.connect(self.display_hint)

        self.hintLabel = QLabel(Dialog)
        self.hintLabel.setGeometry(QtCore.QRect(110, 190, 300, 25))  # Position below passwordForm
        self.hintLabel.setStyleSheet("color: gray; font-style: italic;")
        self.hintLabel.setText("")
        self.hintLabel.hide()  # Hidden initially

        self.imageLabel = QLabel(Dialog)
        self.imageLabel.setGeometry(QtCore.QRect(320, 89, 111, 111))
        self.imageLabel.setObjectName("police_icon")

        pixmap = QtGui.QPixmap(get_img("police.png"))
        scaled_pixmap = pixmap.scaled(self.imageLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.imageLabel.setPixmap(scaled_pixmap)
        self.imageLabel.setAlignment(Qt.AlignCenter)

        self.passwordForm = QLineEdit(Dialog)
        self.passwordForm.setGeometry(QtCore.QRect(110, 160, 191, 25))
        self.passwordForm.setObjectName("lineEdit")
        self.passwordForm.returnPressed.connect(self.try_login)  # ✅ Add this line

        self.labelPassword = QLabel(Dialog)
        self.labelPassword.setGeometry(QtCore.QRect(30, 160, 75, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelPassword.setFont(font)
        self.labelPassword.setObjectName("labelPassword")

        self.labelName = QLabel(Dialog)
        self.labelName.setGeometry(QtCore.QRect(30, 110, 180, 20))
        self.labelName.setFont(font)
        self.labelName.setObjectName("labelName")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        print(f"langauge is {self.language}")
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.loginBtn.setText(_translate("Dialog", "Login"))
        label = get_localized_cfg_entry(self.config, "password_hint_label", self.language, "Passwort Hinweiß")
        self.hintButton.setText(_translate("Dialog", label))
        if self.language != "eng":
            self.labelPassword.setText(_translate("Dialog", "Passwort"))
        else:
            self.labelPassword.setText(_translate("Dialog", "Password"))

        self.labelName.setText(_translate("Dialog", "Name       Christine"))

    def try_login(self):
        entered = self.passwordForm.text()

        if entered.lower() in self.correct_password:
            self.switch_callback()
        else:
            self.passwordForm.clear()
            self.passwordForm.setStyleSheet("border: 2px solid red;")
            self.passwordForm.setPlaceholderText("Falsches Passwort")

    def display_hint(self):
        self.hintLabel.setText(get_localized_cfg_entry(self.config, "password_hint_text", self.language, "Job, Schatz"))  # or any hint you'd like
        self.hintLabel.show()


class PageFinal(QWidget):
    def __init__(self, display_image):
        super().__init__()

        self.display_image = display_image

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # No padding
        layout.setSpacing(0)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: black;")  # Optional

        layout.addWidget(self.image_label)
        self.setLayout(layout)

        self.update_image_fullscreen()

    def update_image_fullscreen(self):
        pixmap = QPixmap(self.display_image)
        if pixmap.isNull():
            print("⚠️ Failed to load image:", self.display_image)
            return

        # Resize image to match the widget's size (which will be fullscreen)
        self.image_label.setPixmap(pixmap.scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))

    def resizeEvent(self, event):
        # Re-scale the image when window is resized (e.g., on launch or resolution change)
        self.update_image_fullscreen()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        try:
            with open('config.json', 'r', encoding='utf8') as config_file:
                self.config = json.load(config_file)
                lowercase_passwords = [p.strip().lower() for p in self.config["password"]]
                self.config["password"] = lowercase_passwords
        except FileNotFoundError:
            exit("config not found, terminating")

        self.language = "deu"
        print("setting default language")
        # Remove window borders and go fullscreen
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()

        self.stack = QStackedWidget()
        self.page1 = PageOne(self.lang_select)
        print(f"going page 2 with {self.language}")
        self.page2 = PageTwo(self.go_to_final, self.language, self.config)
        website_file = get_img(f"website_{self.language}.png")
        print(website_file)
        self.page_final = PageFinal(website_file)

        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)
        self.stack.addWidget(self.page_final)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def lang_select(self, lang):
        print(f"selected language {lang}")
        self.language = lang

        # Remove the old PageTwo if already added
        if self.stack.count() > 1:
            self.stack.removeWidget(self.page2)
            self.page2.deleteLater()

        self.page2 = PageTwo(self.go_to_final, self.language, self.config)
        self.stack.insertWidget(1, self.page2)
        self.stack.setCurrentIndex(1)


    def go_to_final(self):
        self.stack.setCurrentIndex(2)

    @staticmethod
    def keypress_event(event):
        key = event.key()
        modifiers = event.modifiers()

        # Block Alt+Tab, Alt+F4, and Ctrl+Alt+Fx
        if (modifiers & Qt.AltModifier and key in [Qt.Key_Tab, Qt.Key_F4]) or \
                (modifiers & Qt.ControlModifier and modifiers & Qt.AltModifier):
            print("Blocked system key combo")
            return

        # Allow alphanumerics
        if (Qt.Key_0 <= key <= Qt.Key_9) or (Qt.Key_A <= key <= Qt.Key_Z) or key == Qt.Key_Shift:
            print(f"Accepted key: {event.text()}")
        else:
            print(f"Ignored key: {key}")
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


