import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt

class FullscreenApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint)  # Hide window borders
        self.showFullScreen()  # Launch fullscreen

        # Example UI elements
        label = QLabel("Hello from PyQt5!", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 32px;")

        exit_button = QPushButton("Exit")
        exit_button.setStyleSheet("font-size: 20px; padding: 10px;")
        exit_button.clicked.connect(self.close_app)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(exit_button)
        self.setLayout(layout)

    def close_app(self):
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FullscreenApp()
    window.show()
    sys.exit(app.exec_())
