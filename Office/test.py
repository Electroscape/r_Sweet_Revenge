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

import argparse

argparser = argparse.ArgumentParser(
    description='Christines Office')

argparser.add_argument(
    '-c',
    '--city',
    default='s',
    help='name of the city: [hh / s]')



root_path = Path(__file__).parent
img_folder = root_path.joinpath(f"img/{argparser.parse_args().city}")
if not img_folder.exists():
    print(img_folder)
    exit(f"invalid location argument, no image folder found {argparser.parse_args().city}")

def get_img(name):
    return str(img_folder.joinpath(name))


class PageOne(QWidget):
    def __init__(self, switch_callback):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Page 1: Welcome")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 30px;")

        next_btn = QPushButton("Next")
        next_btn.setStyleSheet("font-size: 20px; padding: 10px;")
        next_btn.clicked.connect(switch_callback)

        layout.addWidget(label)
        layout.addWidget(next_btn)
        self.setLayout(layout)

class PageTwo(QWidget):
    def __init__(self, switch_callback):
        super().__init__()
        self.setStyleSheet("background-color: white;")

        self.correct_password = "admin123"  # ✅ Define your expected password
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
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.loginBtn.setText(_translate("Dialog", "Login"))
        self.hintButton.setText(_translate("Dialog", "Passwort vergessen?"))
        self.labelPassword.setText(_translate("Dialog", "Passwort"))
        self.labelName.setText(_translate("Dialog", "Name       Christine"))

    def try_login(self):
        entered = self.passwordForm.text()
        if entered == self.correct_password:
            self.switch_callback()
        else:
            self.passwordForm.clear()
            self.passwordForm.setStyleSheet("border: 2px solid red;")
            self.passwordForm.setPlaceholderText("Falsches Passwort")



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
        # Remove window borders and go fullscreen
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()

        self.stack = QStackedWidget()
        self.page1 = PageOne(self.go_to_page2)
        self.page2 = PageTwo(self.go_to_final)
        self.page_final = PageFinal("website_eng.png")

        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)
        self.stack.addWidget(self.page_final)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def go_to_page2(self):
        self.stack.setCurrentIndex(1)

    def go_to_final(self):
        self.stack.setCurrentIndex(2)

    # Override ESC key to prevent accidental exit
    def keyPressEvent(self, event):
        key = event.key()
        if ((Qt.Key_0 <= key <= Qt.Key_9) or
            (Qt.Key_A <= key <= Qt.Key_Z)
        ):
            print(f"Accepted key: {event.text()}")
        else:
            print(f"Ignored key: {key}")  # Optional: log for debugging
            sleep(1)
            exit("debug exit")
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


