from types import NoneType

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QDialog, QFormLayout
from controllers.auth_controller import AuthController
from windows.admin_window import AdminWindow
from windows.teacher_window import TeacherWindow
from windows.student_window import StudentWindow
import hashlib

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setFixedSize(400, 300)

        self.auth_controller = AuthController()

        self.layout = QVBoxLayout()
        self.login_label = QLabel("Логин:")
        self.login_input = QLineEdit()
        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.handle_login)

        self.create_account_button = QPushButton("Создать аккаунт")
        self.create_account_button.clicked.connect(self.open_create_account_dialog)

        self.layout.addWidget(self.login_label)
        self.layout.addWidget(self.login_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.create_account_button)

        self.setLayout(self.layout)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.attempt_db_connection)
        self.timer.start(30000)

    def attempt_db_connection(self):
        if not self.auth_controller.db.is_connected():
            QMessageBox.critical(self, "Ошибка", "Ошибка при подключении к базе данных")

    def handle_login(self):
        # Получение логина и пароля
        login = self.login_input.text()
        password = self.password_input.text()
        # Хеширование пароля
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        # Попытка авторизации
        try:
            user = self.auth_controller.login(login, hashed_password)
        except:
            QMessageBox.critical(self, "Ошибка", "Ошибка при подключении серверу")
            return
        # Проверка на успешность авторизации
        try:
            if user[2] == 0 and user[3] != "":
                self.show_error_message("Ваш аккаунт заблокирован, обратитесь к администратору")
            elif user[1] == "student":
                self.open_student_window()
            elif user[1] == "teacher":
                self.open_teacher_window()
            elif user[1] == "admin":
                self.open_admin_window()
            else:
                self.show_error_message("Неверный логин или пароль")
        except:
            self.show_error_message("Ошибка при авторизации")

    def open_student_window(self):
        student_info = self.auth_controller.get_student_info(self.login_input.text())
        if student_info:
            self.student_window = StudentWindow(student_info[1])
            self.student_window.show()
            self.close()
        else:
            print("Student information not found.")

    def open_teacher_window(self):
        teacher_info = self.auth_controller.get_teacher_info(self.login_input.text())
        if teacher_info:
            self.teacher_window = TeacherWindow(teacher_info[0])
            self.teacher_window.show()
            self.close()
        else:
            print("Teacher information not found.")

    def open_admin_window(self):
        self.admin_window = AdminWindow()
        self.admin_window.show()
        self.close()

    def show_error_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setText(message)
        msg_box.setWindowTitle("Ошибка")
        msg_box.exec()

    def open_create_account_dialog(self):
        dialog = SetPasswordDialog(self)
        dialog.exec()


class SetPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создание аккаунта")
        self.setGeometry(300, 300, 400, 300)

        layout = QFormLayout()

        self.key_input = QLineEdit()
        self.new_password_input = QLineEdit()
        self.confirm_password_input = QLineEdit()

        layout.addRow("Введите ключ:", self.key_input)
        layout.addRow("Придумайте пароль:", self.new_password_input)
        layout.addRow("Подтвердите пароль:", self.confirm_password_input)

        save_button = QPushButton("Сохранить пароль")
        save_button.clicked.connect(self.set_password)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def set_password(self):
        key = self.key_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if len(new_password) < 8 or not any(char.isdigit() for char in new_password):
            QMessageBox.critical(self, "Ошибка", "Пароль должен быть минимум 8 символов и содержать хотя бы одну цифру")
            return

        if new_password != confirm_password:
            QMessageBox.critical(self, "Ошибка", "Пароли не совпадают")
            return

        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

        if self.parent().auth_controller.set_password(key, hashed_password):
            QMessageBox.information(self, "Успех", "Пароль успешно установлен")
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "Ошибка при установке пароля")