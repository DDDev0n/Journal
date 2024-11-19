from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget, QDialog, QFormLayout, QLineEdit, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QInputDialog
from windows.base_window import BaseWindow
from controllers.schedule_controller import ScheduleController
from controllers.db_controller import DBController
from controllers.groups_controller import GroupsController

class AdminWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Админская панель")

        self.schedule_controller = ScheduleController()
        self.db_controller = DBController()
        self.groups_controller = GroupsController()

        self.init_ui()

    def init_ui(self):
        # Set the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Check if layout is already set
        if not self.central_widget.layout():
            self.layout = QVBoxLayout()
            self.central_widget.setLayout(self.layout)

        self.label = QLabel("Добро пожаловать, Администратор!")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)

        self.create_teacher_account_button = QPushButton("Создать аккаунт преподавателя")
        self.create_teacher_account_button.clicked.connect(self.open_create_teacher_account_dialog)
        self.layout.addWidget(self.create_teacher_account_button)

        self.manage_groups_button = QPushButton("Управление группами")
        self.manage_groups_button.clicked.connect(self.open_manage_groups_dialog)
        self.layout.addWidget(self.manage_groups_button)

        self.manage_schedule_button = QPushButton("Управление расписанием")
        self.manage_schedule_button.clicked.connect(self.open_manage_schedule_dialog)
        self.layout.addWidget(self.manage_schedule_button)

    def open_create_teacher_account_dialog(self):
        dialog = CreateAccountDialog(self, role="teacher")
        dialog.exec()

    def open_manage_groups_dialog(self):
        dialog = ManageGroupsDialog(self)
        dialog.exec()

    def open_manage_schedule_dialog(self):
        dialog = ManageScheduleDialog(self)
        dialog.exec()


class CreateAccountDialog(QDialog):
    def __init__(self, parent=None, role=None, group_id=None, db_controller=None):
        super().__init__(parent)
        self.setWindowTitle("Создать аккаунт")
        self.setGeometry(300, 300, 400, 300)

        self.role = role
        self.group_id = group_id
        self.db_controller = db_controller  # Accept db_controller

        layout = QFormLayout()

        self.login_input = QLineEdit()
        self.first_name_input = QLineEdit()
        self.middle_name_input = QLineEdit()
        self.last_name_input = QLineEdit()

        layout.addRow("Логин:", self.login_input)
        layout.addRow("Имя:", self.first_name_input)
        layout.addRow("Фамилия:", self.last_name_input)
        layout.addRow("Отчество:", self.middle_name_input)

        save_button = QPushButton("Создать аккаунт")
        save_button.clicked.connect(self.create_account)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def create_account(self):
        login = self.login_input.text()
        first_name = self.first_name_input.text()
        middle_name = self.middle_name_input.text()
        last_name = self.last_name_input.text()
        group = self.group_id if self.role == "student" else None

        password = self.db_controller.create_account(login, first_name, middle_name, last_name, self.role, group)
        if password:
            QMessageBox.information(self, "Аккаунт создан", f"Аккаунт успешно создан. Ваш пароль: {password}")
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "Ошибка при создании аккаунта")


class ManageGroupsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Управление группами")
        self.setGeometry(300, 300, 400, 300)

        self.groups_controller = parent.groups_controller
        self.db_controller = parent.db_controller  # Pass db_controller

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.group_table = QTableWidget()
        self.group_table.setColumnCount(2)
        self.group_table.setHorizontalHeaderLabels(["ID", "Название группы"])
        self.group_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.group_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.group_table.itemSelectionChanged.connect(self.on_group_selected)
        self.layout.addWidget(self.group_table)

        self.create_group_button = QPushButton("Создать группу")
        self.create_group_button.clicked.connect(self.create_group)
        self.layout.addWidget(self.create_group_button)

        self.create_student_button = QPushButton("Создать студента")
        self.create_student_button.setEnabled(False)
        self.create_student_button.clicked.connect(self.open_create_student_account_dialog)
        self.layout.addWidget(self.create_student_button)

        self.view_students_button = QPushButton("Посмотреть студентов")
        self.view_students_button.setEnabled(False)
        self.view_students_button.clicked.connect(self.view_students)
        self.layout.addWidget(self.view_students_button)

        self.edit_group_button = QPushButton("Редактировать название группы")
        self.edit_group_button.setEnabled(False)
        self.edit_group_button.clicked.connect(self.edit_group_name)
        self.layout.addWidget(self.edit_group_button)

        self.update_group_list()  # Update the group list when the dialog is initialized

    def update_group_list(self):
        self.group_table.setRowCount(0)
        groups = self.groups_controller.get_groups()
        for group in groups:
            row_position = self.group_table.rowCount()
            self.group_table.insertRow(row_position)
            id_item = QTableWidgetItem(str(group[0]))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item = QTableWidgetItem(group[1])
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.group_table.setItem(row_position, 0, id_item)
            self.group_table.setItem(row_position, 1, name_item)

    def create_group(self):
        group_name, ok = QInputDialog.getText(self, "Создать группу", "Название группы:")
        if ok and group_name:
            self.groups_controller.create_group(group_name)
            self.update_group_list()
            QMessageBox.information(self, "Успех", "Группа успешно создана")
        else:
            QMessageBox.critical(self, "Ошибка", "Введите название группы")

    def on_group_selected(self):
        selected_items = self.group_table.selectedItems()
        self.create_student_button.setEnabled(bool(selected_items))
        self.view_students_button.setEnabled(bool(selected_items))
        self.edit_group_button.setEnabled(bool(selected_items))

    def open_create_student_account_dialog(self):
        selected_items = self.group_table.selectedItems()
        if selected_items:
            group_id = int(selected_items[0].text())
            dialog = CreateAccountDialog(self, role="student", group_id=group_id, db_controller=self.db_controller)
            dialog.exec()
        else:
            QMessageBox.critical(self, "Ошибка", "Выберите группу")

    def view_students(self):
        selected_items = self.group_table.selectedItems()
        if selected_items:
            group_id = int(selected_items[0].text())
            dialog = ViewStudentsDialog(self, group_id=group_id)
            dialog.exec()
        else:
            QMessageBox.critical(self, "Ошибка", "Выберите группу")

    def edit_group_name(self):
        selected_items = self.group_table.selectedItems()
        if selected_items:
            group_id = int(selected_items[0].text())
            current_name = selected_items[1].text()
            new_name, ok = QInputDialog.getText(self, "Редактировать название группы", "Новое название группы:", text=current_name)
            if ok and new_name:
                self.groups_controller.update_group_name(group_id, new_name)
                self.update_group_list()
                QMessageBox.information(self, "Успех", "Название группы успешно обновлено")
            else:
                QMessageBox.critical(self, "Ошибка", "Введите новое название группы")


class ManageScheduleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Управление расписанием")
        self.setGeometry(300, 300, 400, 300)

        self.schedule_controller = parent.schedule_controller

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(5)
        self.schedule_table.setHorizontalHeaderLabels(["Группа", "Дата", "Время", "Предмет", "Преподаватель"])
        self.load_schedule()
        self.layout.addWidget(self.schedule_table)

        self.add_schedule_button = QPushButton("Добавить расписание")
        self.add_schedule_button.clicked.connect(self.open_add_schedule_dialog)
        self.layout.addWidget(self.add_schedule_button)

    def load_schedule(self):
        schedule_data = self.schedule_controller.get_schedule()
        self.schedule_table.setRowCount(len(schedule_data))
        for row, item in enumerate(schedule_data):
            for col, value in enumerate(item):
                self.schedule_table.setItem(row, col, QTableWidgetItem(str(value)))

    def open_add_schedule_dialog(self):
        dialog = AddScheduleDialog(self)
        dialog.exec()

class AddScheduleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить расписание")
        self.setGeometry(300, 300, 400, 300)

        layout = QFormLayout()

        self.group_input = QLineEdit()
        self.date_input = QLineEdit()
        self.time_input = QLineEdit()
        self.subject_input = QLineEdit()
        self.teacher_input = QLineEdit()

        layout.addRow("Группа:", self.group_input)
        layout.addRow("Дата:", self.date_input)
        layout.addRow("Время:", self.time_input)
        layout.addRow("Предмет:", self.subject_input)
        layout.addRow("Преподаватель:", self.teacher_input)

        save_button = QPushButton("Добавить")
        save_button.clicked.connect(self.add_schedule)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def add_schedule(self):
        group = self.group_input.text()
        date = self.date_input.text()
        time = self.time_input.text()
        subject = self.subject_input.text()
        teacher = self.teacher_input.text()

        QMessageBox.information(self, "Успех", "Расписание успешно добавлено")
        self.accept()

class ViewStudentsDialog(QDialog):
    def __init__(self, parent=None, group_id=None):
        super().__init__(parent)
        self.setWindowTitle("Студенты группы")
        self.setGeometry(300, 300, 400, 300)

        self.group_id = group_id
        self.groups_controller = parent.groups_controller

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.students_table = QTableWidget()
        self.students_table.setColumnCount(3)
        self.students_table.setHorizontalHeaderLabels(["ID", "Имя", "Фамилия"])
        self.layout.addWidget(self.students_table)

        self.load_students()

    def load_students(self):
        students = self.groups_controller.get_students_in_group(self.group_id)
        self.students_table.setRowCount(len(students))
        for row, student in enumerate(students):
            id_item = QTableWidgetItem(str(student[0]))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item = QTableWidgetItem(student[1])
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            surname_item = QTableWidgetItem(student[2])
            surname_item.setFlags(surname_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.students_table.setItem(row, 0, id_item)
            self.students_table.setItem(row, 1, name_item)
            self.students_table.setItem(row, 2, surname_item)