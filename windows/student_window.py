from PyQt6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QPushButton
from PyQt6.QtCore import Qt
from controllers.groups_controller import GroupsController
from controllers.db_controller import DBController

class StudentWindow(QMainWindow):
    def __init__(self, group_id):
        super().__init__()
        self.setWindowTitle("Расписание студента")
        self.resize(1000, 600)

        self.db_controller = DBController()
        if not self.db_controller.is_connected():
            QMessageBox.critical(self, "Database Error", "Failed to connect to the database")
            return

        self.groups_controller = GroupsController(self.db_controller)
        self.group_id = group_id

        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        if not self.central_widget.layout():
            self.layout = QVBoxLayout()
            self.central_widget.setLayout(self.layout)

        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.button_layout.addStretch()

        self.logout_button = QPushButton("Выйти с аккаунта")
        self.logout_button.clicked.connect(self.handle_logout)
        self.button_layout.addWidget(self.logout_button)

        self.schedule_table = QTableWidget()
        self.layout.addWidget(self.schedule_table)

        self.load_schedule()

    def load_schedule(self):
        # Получения расписания группы по их id
        schedule = self.groups_controller.get_group_schedule(self.group_id)
        # Отправка расписания на форматирование
        formatted_schedule = self.format_schedule(schedule)
        # Создание таблицы
        self.schedule_table.setRowCount(len(formatted_schedule))
        self.schedule_table.setColumnCount(6)
        self.schedule_table.setHorizontalHeaderLabels(['Группа', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница'])
        # Внесение данных в таблицу
        for row_idx, row_data in enumerate(formatted_schedule):
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.schedule_table.setItem(row_idx, col_idx, item)
        # Форматирование таблицы
        for col in range(6):
            self.schedule_table.setColumnWidth(col, 150)

    def format_schedule(self, schedule_data):
        formatted_data = []
        current_group = None
        dataOut = []

        for row in schedule_data:
            group_name, day, *subjects = row
            if group_name != current_group:
                if current_group is not None:
                    for j in range(len(dataOut)):
                        formatted_data.append(dataOut[j])
                    formatted_data.append([''] * 6)

                dataOut = [[''] * 6 for _ in range(5)]
                formatted_data.append([group_name, 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница'])
                current_group = group_name

            if day in self.groups_controller.days:
                for i, subject in enumerate(subjects):
                    if subject:
                        dataOut[i][0] = i + 1
                        dataOut[i][1 + self.groups_controller.days.index(day)] = subject
            else:
                print(f"Warning: {day} is not a valid day")

        if dataOut:
            for j in range(len(dataOut)):
                if dataOut[j][0] == '':
                    dataOut[j][0] = j + 1
                formatted_data.append(dataOut[j])

        return formatted_data

    def handle_logout(self):
        from windows.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()