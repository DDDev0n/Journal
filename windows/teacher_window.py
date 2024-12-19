from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from windows.base_window import BaseWindow
from controllers.teachers_controller import TeachersController

class TeacherWindow(BaseWindow):
    def __init__(self, teacher_id):
        super().__init__()
        self.setWindowTitle("Расписание учителя")
        self.resize(1000, 600)

        self.teachers_controller = TeachersController()

        self.teacher_id = teacher_id

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
        schedule = self.teachers_controller.get_teacher_schedule(self.teacher_id)
        formatted_schedule = self.format_schedule(schedule)
        self.schedule_table.setRowCount(len(formatted_schedule))
        self.schedule_table.setColumnCount(6)
        self.schedule_table.setHorizontalHeaderLabels(
            ['Преподаватель', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница'])

        for row_idx, row_data in enumerate(formatted_schedule):
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.schedule_table.setItem(row_idx, col_idx, item)

        for col in range(6):
            self.schedule_table.setColumnWidth(col, 150)

    def format_schedule(self, schedule_data):
        formatted_data = []
        current_teacher = None
        dataOut = []

        for row in schedule_data:
            teacher_name, day, *subjects = row
            if teacher_name != current_teacher:
                if current_teacher is not None:
                    for j in range(len(dataOut)):
                        formatted_data.append(dataOut[j])
                    formatted_data.append([''] * 6)

                dataOut = [[''] * 6 for _ in range(5)]
                formatted_data.append([teacher_name, 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница'])
                current_teacher = teacher_name

            if day in self.teachers_controller.days:
                for i, subject in enumerate(subjects):
                    if subject:
                        dataOut[i][0] = i + 1
                        dataOut[i][1 + self.teachers_controller.days.index(day)] = subject
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