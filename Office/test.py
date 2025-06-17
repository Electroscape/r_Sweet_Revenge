# @author Martin Pek (martin.pek@web.de)

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QStackedWidget
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from time import sleep

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
        layout = QVBoxLayout()
        label = QLabel("Page 2: Second Layer")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 30px;")

        back_btn = QPushButton("Back")
        back_btn.setStyleSheet("font-size: 20px; padding: 10px;")
        back_btn.clicked.connect(switch_callback)

        layout.addWidget(label)
        layout.addWidget(back_btn)
        self.setLayout(layout)

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

