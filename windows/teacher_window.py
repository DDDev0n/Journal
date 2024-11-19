from PyQt6.QtWidgets import QLabel
from windows.base_window import BaseWindow
from PyQt6.QtCore import Qt

class TeacherWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Окно преподавателя")

        self.label = QLabel("Добро пожаловать, Преподаватель!")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.label)
