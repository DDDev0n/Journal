from controllers.db_controller import DBController

class AuthController:
    def __init__(self):
        self.db = DBController()

    def login(self, login, password):
        with self.db.connection.cursor() as cursor:
            query = """
            SELECT u.Id_user, r.Name, u.Activated, u.Pas AS role
            FROM Users u
            JOIN Roles r ON u.Id_role = r.Id_role
            WHERE BINARY u.Login = %s AND BINARY u.Pas = %s
            """
            cursor.execute(query, (login, password))
            user = cursor.fetchone()
            if user:
                return user
            else:
                return None

    def set_password(self, key, new_password):
        with self.db.connection.cursor() as cursor:
            cursor.execute("SELECT Id_user FROM Users WHERE CreateCode = %s", (key,))
            result = cursor.fetchone()
            if result:
                user_id = result[0]
                cursor.execute("UPDATE Users SET Pas = %s, Activated = True WHERE Id_user = %s", (new_password, user_id))
                self.db.connection.commit()
                return True
            else:
                return False

    def get_student_info(self, login):
        with self.db.connection.cursor() as cursor:
            query = "SELECT Id_student, Id_group FROM Student WHERE Id_user = (SELECT Id_user FROM Users WHERE Login = %s)"
            cursor.execute(query, (login,))
            return cursor.fetchone()

    def get_teacher_info(self, login):
        try:
            with self.db.connection.cursor() as cursor:
                query = """SELECT Id_user FROM Users WHERE Login = %s
                """
                cursor.execute(query, (login,))
                teacher_info = cursor.fetchone()
                return teacher_info
        except Exception as e:
            print(f"Error retrieving teacher information: {e}")
            return None