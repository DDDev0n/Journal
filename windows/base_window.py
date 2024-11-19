from PyQt6.QtWidgets import QMainWindow

class BaseWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Schedule App")
        self.setGeometry(100, 100, 800, 600)
