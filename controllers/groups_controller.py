from PyQt6.QtWidgets import QMessageBox

class GroupsController:
    def __init__(self, db_controller):
        self.db = db_controller
        self.days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']

    def create_group(self, group_name):
        with self.db.connection.cursor() as cursor:
            cursor.execute("INSERT INTO `Groups` (Group_name) VALUES (%s)", (group_name,))
            self.db.connection.commit()

    def get_groups(self):
        with self.db.connection.cursor() as cursor:
            cursor.execute("SELECT Id_group, Group_name FROM `Groups`")
            return cursor.fetchall()

    def get_students_in_group(self, group_id):
        with self.db.connection.cursor() as cursor:
            cursor.execute("SELECT Id_student, Name, Surname, Middle_Name FROM `Student` WHERE Id_group = %s", (group_id,))
            return cursor.fetchall()

    def update_group_name(self, group_id, new_name):
        with self.db.connection.cursor() as cursor:
            cursor.execute("UPDATE `Groups` SET Group_name = %s WHERE Id_group = %s", (new_name, group_id))
            self.db.connection.commit()

    def remove_student_from_group(self, student_id):
        with self.db.connection.cursor() as cursor:
            query = "UPDATE Users SET Activated = false WHERE Id_user = (SELECT Id_user FROM Student where Id_student = %s)"
            cursor.execute(query, (student_id,))
            query = "UPDATE Student SET id_group = null WHERE Id_student = %s"
            cursor.execute(query, (student_id,))
            self.db.connection.commit()

    def full_remove_student_from_group(self, student_id):
        with self.db.connection.cursor() as cursor:
            query = "DELETE FROM Users WHERE Id_user = (SELECT Id_user FROM Student where Id_student = %s)"
            cursor.execute(query, (student_id,))
            query = "DELETE FROM Student WHERE Id_student = %s"
            cursor.execute(query, (student_id,))
            self.db.connection.commit()

    def check_status(self, student_id):
        with self.db.connection.cursor() as cursor:
            cursor.execute("SELECT Activated FROM `Users` WHERE Id_user = (SELECT Id_user FROM Student where Id_student = %s)", (student_id,))
            return cursor.fetchall()

    def transfer_student_to_group(self, student_id, new_group_id):
        with self.db.connection.cursor() as cursor:
            query = "UPDATE Student SET Id_group = %s WHERE Id_student = %s"
            cursor.execute(query, (new_group_id, student_id))
            self.db.connection.commit()

    def get_group_schedule(self, group_id):
        if not self.db.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return []

        try:
            with self.db.connection.cursor() as cursor:
                query = """
                    SELECT g.Group_name, s.day, sub1.Specialization_name, sub2.Specialization_name, sub3.Specialization_name, sub4.Specialization_name, sub5.Specialization_name
                    FROM Schedule s
                    JOIN `Groups` g ON s.Id_group = g.Id_group
                    LEFT JOIN Specializations sub1 ON s.subj1 = sub1.Id_specialization
                    LEFT JOIN Specializations sub2 ON s.subj2 = sub2.Id_specialization
                    LEFT JOIN Specializations sub3 ON s.subj3 = sub3.Id_specialization
                    LEFT JOIN Specializations sub4 ON s.subj4 = sub4.Id_specialization
                    LEFT JOIN Specializations sub5 ON s.subj5 = sub5.Id_specialization
                    WHERE s.Id_group = %s
                """
                cursor.execute(query, (group_id,))
                rows = cursor.fetchall()
                schedule_data = []
                for row in rows:
                    schedule_data.append(list(row))
                return schedule_data
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return []

    def get_group_name_by_id(self, group_id):
        with self.db.connection.cursor() as cursor:
            cursor.execute("SELECT Group_name FROM `Groups` WHERE Id_group = %s", (group_id,))
            result = cursor.fetchone()
            return result[0] if result else ""

    def get_subject_name_by_id(self, subject_id):
        with self.db.connection.cursor() as cursor:
            cursor.execute("SELECT Subject_name FROM `Subjects` WHERE Id_subject = %s", (subject_id,))
            result = cursor.fetchone()
            return result[0] if result else ""