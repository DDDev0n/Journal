import pymysql
import random
import string
from PyQt6.QtWidgets import QMessageBox

class DBController:
    def __init__(self):
        try:
            self.connection = pymysql.connect(
                host="88.84.204.195",
                port=3307,
                user="admin",
                password="f2300a1554e7095209f4cdd81dcb883cc34f59d7f9c43008a74eae6935359a33",
                database="StudentSchedule",
                connect_timeout=40
            )
        except pymysql.MySQLError as e:
            QMessageBox.critical(None, "Database Error", f"Database connection error: {e}")
            self.connection = None

    def is_connected(self):
        return self.connection is not None

    def get_user(self, login, password):
        if not self.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return None

        try:
            with self.connection.cursor() as cursor:
                query = """
                SELECT u.Login, r.Name AS role
                FROM Users u
                JOIN Roles r ON u.Id_role = r.Id_role
                WHERE u.Login=%s AND u.Pas=%s
                """
                cursor.execute(query, (login, password))
                result = cursor.fetchone()
                return {"login": result[0], "role": result[1]} if result else None
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return None

    def get_schedule(self):
        if not self.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return []

        try:
            with self.connection.cursor() as cursor:
                query = """
                SELECT g.Group_name, s.Date, s.Start_time, s.End_time, s.Subject, t.Name
                FROM `Schedule` s
                JOIN `Groups` g ON s.Id_group = g.Id_group
                JOIN `Teacher` t ON s.Teacher_id = t.Id_user
                """
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return []

    def add_schedule(self, group, date, start_time, end_time, subject, teacher_id):
        if not self.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return False

        try:
            with self.connection.cursor() as cursor:
                query = """
                INSERT INTO Schedule (Id_group, Date, Start_time, End_time, Subject, Teacher_id)
                VALUES ((SELECT Id_group FROM Groups WHERE Group_name = %s), %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (group, date, start_time, end_time, subject, teacher_id))
                self.connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return False

    def get_teachers(self):
        if not self.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return []

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT Id_user, Name, Surname FROM Teacher")
                return cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return []

    def get_teacher_id_by_name(self, teacher_name):
        if not self.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return None

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT Id_user FROM Teacher WHERE Name = %s", (teacher_name,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return None

    def generate_random_code(self, length=16):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(length))

    def create_account(self, login, first_name, middle_name, last_name, role, group_id=None):
        if not self.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return None

        try:
            with self.connection.cursor() as cursor:
                create_code = self.generate_random_code()
                cursor.execute("""
                    INSERT INTO Users (Login, CreateCode, Id_role)
                    VALUES (%s, %s, (SELECT Id_role FROM Roles WHERE Name = %s))
                """, (login, create_code, role))
                user_id = cursor.lastrowid

                if role == "student":
                    cursor.execute("""
                        INSERT INTO Student (Id_user, Name, Middle_name, Surname, Id_group)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (user_id, first_name, middle_name, last_name, group_id))
                elif role == "teacher":
                    cursor.execute("""
                        INSERT INTO Teacher (Id_user, Name, Middle_name, Surname)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, first_name, middle_name, last_name))

                self.connection.commit()
                return create_code
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during account creation: {e}")
            self.connection.rollback()
            return None

    def get_specializations(self):
        if not self.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return []

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT Id_specialization, Specialization_name FROM Specializations")
                return cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return []

    def add_specialization(self, specialization_name):
        if not self.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return False

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("INSERT INTO Specializations (Specialization_name) VALUES (%s)", (specialization_name,))
                self.connection.commit()
                return True
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return False

    def get_teacher_specializations(self, teacher_id):
        if not self.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return []

        try:
            with self.connection.cursor() as cursor:
                query = """
                SELECT s.Id_specialization, s.Specialization_name
                FROM TeacherSpecializations ts
                JOIN Specializations s ON ts.Id_specialization = s.Id_specialization
                WHERE ts.Id_teacher = %s
                """
                cursor.execute(query, (teacher_id,))
                return cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return []

    def add_teacher_specialization(self, teacher_id, specialization_id):
        if not self.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return False

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("INSERT INTO TeacherSpecializations (Id_teacher, Id_specialization) VALUES (%s, %s)",
                               (teacher_id, specialization_id))
                self.connection.commit()
                return True
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return False

    def remove_teacher_specialization(self, teacher_id, specialization_id):
        if not self.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return False

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM TeacherSpecializations WHERE Id_teacher = %s AND Id_specialization = %s",
                               (teacher_id, specialization_id))
                self.connection.commit()
                return True
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return False

    def get_specialization_id_by_name(self, specialization_name):
        if not self.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return None

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT Id_specialization FROM Specializations WHERE Specialization_name = %s",
                               (specialization_name,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return None

    def get_group_teachers(self, group_id):
        if not self.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return []

        try:
            with self.connection.cursor() as cursor:
                query = """
                SELECT s.Specialization_name, CONCAT(t.Name, ' ', t.Surname)
                FROM Groups_Specialization_teacher gst
                JOIN Specializations s ON gst.Specialization_id = s.Id_specialization
                JOIN Teacher t ON gst.Teacher_id = t.Id_user
                WHERE gst.Group_id = %s
                """
                cursor.execute(query, (group_id,))
                return cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return []

    def get_teachers_by_specialization(self, specialization_id):
        if not self.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return []

        try:
            with self.connection.cursor() as cursor:
                query = """
                SELECT t.Id_user, t.Name, t.Surname
                FROM TeacherSpecializations ts
                JOIN Teacher t ON ts.Id_teacher = t.Id_user
                WHERE ts.Id_specialization = %s
                """
                cursor.execute(query, (specialization_id,))
                return cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return []

    def assign_teacher_to_group(self, group_id, subject_id, teacher_id):
        if not self.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return

        try:
            query = """
            INSERT INTO Groups_Specialization_teacher (Group_id, Specialization_id, Teacher_id)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE Teacher_id = VALUES(Teacher_id)
            """
            with self.connection.cursor() as cursor:
                cursor.execute(query, (group_id, subject_id, teacher_id))
                self.connection.commit()
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")

    def get_schedule(self, group_id):
        if not self.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return []

        try:
            query = """
            SELECT
                sch.Id_schedule,
                grp.Group_name,
                sch.day,
                CONCAT(sp1.Specialization_name, ' - ', t1.Name, ' ', t1.Surname) AS subj1,
                CONCAT(sp2.Specialization_name, ' - ', t2.Name, ' ', t2.Surname) AS subj2,
                CONCAT(sp3.Specialization_name, ' - ', t3.Name, ' ', t3.Surname) AS subj3,
                CONCAT(sp4.Specialization_name, ' - ', t4.Name, ' ', t4.Surname) AS subj4,
                CONCAT(sp5.Specialization_name, ' - ', t5.Name, ' ', t5.Surname) AS subj5
            FROM
                Schedule sch
            JOIN
                `Groups` grp ON sch.Id_group = grp.Id_group
            LEFT JOIN
                Specializations sp1 ON sch.subj1 = sp1.Id_specialization
            LEFT JOIN
                Groups_Specialization_teacher gst1 ON sch.Id_group = gst1.Group_id AND sch.subj1 = gst1.Specialization_id
            LEFT JOIN
                Teacher t1 ON gst1.Teacher_id = t1.Id_user
            LEFT JOIN
                Specializations sp2 ON sch.subj2 = sp2.Id_specialization
            LEFT JOIN
                Groups_Specialization_teacher gst2 ON sch.Id_group = gst2.Group_id AND sch.subj2 = gst2.Specialization_id
            LEFT JOIN
                Teacher t2 ON gst2.Teacher_id = t2.Id_user
            LEFT JOIN
                Specializations sp3 ON sch.subj3 = sp3.Id_specialization
            LEFT JOIN
                Groups_Specialization_teacher gst3 ON sch.Id_group = gst3.Group_id AND sch.subj3 = gst3.Specialization_id
            LEFT JOIN
                Teacher t3 ON gst3.Teacher_id = t3.Id_user
            LEFT JOIN
                Specializations sp4 ON sch.subj4 = sp4.Id_specialization
            LEFT JOIN
                Groups_Specialization_teacher gst4 ON sch.Id_group = gst4.Group_id AND sch.subj4 = gst4.Specialization_id
            LEFT JOIN
                Teacher t4 ON gst4.Teacher_id = t4.Id_user
            LEFT JOIN
                Specializations sp5 ON sch.subj5 = sp5.Id_specialization
            LEFT JOIN
                Groups_Specialization_teacher gst5 ON sch.Id_group = gst5.Group_id AND sch.subj5 = gst5.Specialization_id
            LEFT JOIN
                Teacher t5 ON gst5.Teacher_id = t5.Id_user
            WHERE
                grp.Id_group = %s
            """
            with self.connection.cursor() as cursor:
                cursor.execute(query, (group_id,))
                return cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return []

    def save_group_schedule(self, group_id, schedule_data):
        if not self.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return False

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM Schedule WHERE Id_group = %s", (group_id,))
                for day, subjects in schedule_data.items():
                    cursor.execute(
                        """
                        INSERT INTO Schedule (Id_group, day, subj1, subj2, subj3, subj4, subj5)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (group_id, day, subjects[0], subjects[1], subjects[2], subjects[3], subjects[4])
                    )
                self.connection.commit()
                return True
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return False

    def load_group_schedule(self, group_id):
        if not self.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return {}

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT day, subj1, subj2, subj3, subj4, subj5 FROM Schedule WHERE Id_group = %s",
                               (group_id,))
                rows = cursor.fetchall()
                schedule_data = {day: [None] * 5 for day in ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']}
                for row in rows:
                    day, subj1, subj2, subj3, subj4, subj5 = row
                    schedule_data[day] = [subj1, subj2, subj3, subj4, subj5]
                return schedule_data
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return {}

    def remove_teacher_from_group(self, group_id, subject_id):
        try:
            with self.connection.cursor() as cursor:
                query = """
                DELETE FROM Groups_Specialization_teacher
                WHERE Group_id = %s AND Specialization_id = %s
                """
                cursor.execute(query, (group_id, subject_id))
                self.connection.commit()
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")

    def is_teacher_assigned(self, group_id, subject_id):
        if not self.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return False

        try:
            with self.connection.cursor() as cursor:
                query = """
                SELECT COUNT(*)
                FROM Groups_Specialization_teacher
                WHERE Group_id = %s AND Specialization_id = %s
                """
                cursor.execute(query, (group_id, subject_id))
                result = cursor.fetchone()
                return result[0] > 0
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return False

    def is_teacher_busy(self, group_id, subject_id, day, period):
        if not self.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return True

        try:
            with self.connection.cursor() as cursor:
                query = """
                SELECT COUNT(*)
                FROM Schedule sch
                JOIN Groups_Specialization_teacher gst ON sch.Id_group = gst.Group_id AND sch.subj{period} = gst.Specialization_id
                WHERE gst.Teacher_id = (SELECT Teacher_id FROM Groups_Specialization_teacher WHERE Group_id = %s AND Specialization_id = %s)
                AND sch.day = %s AND sch.Id_group != %s
                """.format(period=period)
                cursor.execute(query, (group_id, subject_id, day, group_id))
                result = cursor.fetchone()
                return result[0] > 0
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return True