from PyQt6.QtWidgets import QLabel
from windows.base_window import BaseWindow
from PyQt6.QtCore import Qt

class StudentWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Окно студента")

        self.label = QLabel("Добро пожаловать, Студент!")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.label)
