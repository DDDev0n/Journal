import pymysql
import random
import string

class DBController:
    def __init__(self):
        try:
            self.connection = pymysql.connect(
                host="localhost",       # Локальный хост, если Docker работает локально
                port=3307,              # Учитываем порт из docker-compose.yml
                user="admin",           # Пользователь из environment
                password="admin_228",   # Пароль пользователя из environment
                database="StudentSchedule"
            )
        except pymysql.MySQLError as e:
            print(f"Database connection error: {e}")
            self.connection = None

    def get_user(self, login, password):
        if not self.connection:
            print("Database connection not established")
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
            print(f"Error during DB query: {e}")
            return None

    def get_schedule(self):
        with self.connection.cursor() as cursor:
            query = """
            SELECT g.Group_name, s.Date, s.Start_time, s.End_time, s.Subject, t.Name
            FROM `Schedule` s
            JOIN `Groups` g ON s.Id_group = g.Id_group
            JOIN `Teacher` t ON s.Teacher_id = t.Id_user
            """
            cursor.execute(query)
            return cursor.fetchall()

    def add_schedule(self, group, date, start_time, end_time, subject, teacher_id):
        with self.connection.cursor() as cursor:
            query = """
            INSERT INTO Schedule (Id_group, Date, Start_time, End_time, Subject, Teacher_id)
            VALUES ((SELECT Id_group FROM Groups WHERE Group_name = %s), %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (group, date, start_time, end_time, subject, teacher_id))
            self.connection.commit()
            return cursor.rowcount > 0

    def get_teachers(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT Id_user, Name FROM Teacher")
            return cursor.fetchall()

    def get_teacher_id_by_name(self, teacher_name):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT Id_user FROM Teacher WHERE Name = %s", (teacher_name,))
            result = cursor.fetchone()
            return result[0] if result else None

    def generate_random_code(self, length=16):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(length))

    def create_account(self, login, first_name, middle_name, last_name, role, group_id=None):
        with self.connection.cursor() as cursor:
            try:
                # Генерация случайного кода
                create_code = self.generate_random_code()

                # Вставка в таблицу Users
                cursor.execute("""
                    INSERT INTO Users (Login, CreateCode, Id_role)
                    VALUES (%s, %s, (SELECT Id_role FROM Roles WHERE Name = %s))
                """, (login, create_code, role))
                user_id = cursor.lastrowid

                # Вставка в таблицу Student или Teacher в зависимости от роли
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
                print(f"Error during account creation: {e}")
                self.connection.rollback()
                return None

    def get_teachers(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT Id_user, Name, Surname FROM Teacher")
            return cursor.fetchall()

    def get_specializations(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT Id_specialization, Specialization_name FROM Specializations")
            return cursor.fetchall()

    def add_specialization(self, specialization_name):
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO Specializations (Specialization_name) VALUES (%s)", (specialization_name,))
            self.connection.commit()

    def get_teacher_specializations(self, teacher_id):
        with self.connection.cursor() as cursor:
            query = """
            SELECT s.Id_specialization, s.Specialization_name
            FROM TeacherSpecializations ts
            JOIN Specializations s ON ts.Id_specialization = s.Id_specialization
            WHERE ts.Id_teacher = %s
            """
            cursor.execute(query, (teacher_id,))
            return cursor.fetchall()

    def add_teacher_specialization(self, teacher_id, specialization_id):
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO TeacherSpecializations (Id_teacher, Id_specialization) VALUES (%s, %s)",
                           (teacher_id, specialization_id))
            self.connection.commit()

    def remove_teacher_specialization(self, teacher_id, specialization_id):
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM TeacherSpecializations WHERE Id_teacher = %s AND Id_specialization = %s",
                           (teacher_id, specialization_id))
            self.connection.commit()

    def get_specialization_id_by_name(self, specialization_name):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT Id_specialization FROM Specializations WHERE Specialization_name = %s",
                               (specialization_name,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Error during DB query: {e}")
            return None

    def get_group_teachers(self, group_id):
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

    def get_teachers_by_specialization(self, specialization_id):
        with self.connection.cursor() as cursor:
            query = """
            SELECT t.Id_user, t.Name, t.Surname
            FROM TeacherSpecializations ts
            JOIN Teacher t ON ts.Id_teacher = t.Id_user
            WHERE ts.Id_specialization = %s
            """
            cursor.execute(query, (specialization_id,))
            return cursor.fetchall()

    def assign_teacher_to_group(self, group_id, specialization_id, teacher_id):
        with self.connection.cursor() as cursor:
            query = """
            INSERT INTO Groups_Specialization_teacher (Group_id, Specialization_id, Teacher_id)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (group_id, specialization_id, teacher_id))
            self.connection.commit()