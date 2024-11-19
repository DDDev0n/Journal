from controllers.db_controller import DBController

class AuthController:
    def __init__(self):
        self.db = DBController()

    def login(self, login, password):
        with self.db.connection.cursor() as cursor:
            query = """
            SELECT u.Id_user, r.Name AS role
            FROM Users u
            JOIN Roles r ON u.Id_role = r.Id_role
            WHERE BINARY u.Login = %s AND BINARY u.Pas = %s
            """
            cursor.execute(query, (login, password))
            user = cursor.fetchone()
            if user:
                return user[1]  # Assuming the role is the second column
            else:
                return None

    def set_password(self, key, new_password):
        with self.db.connection.cursor() as cursor:
            cursor.execute("SELECT Id_user FROM Users WHERE CreateCode = %s", (key,))
            result = cursor.fetchone()
            if result:
                user_id = result[0]
                cursor.execute("UPDATE Users SET Pas = %s, CreateCode = NULL WHERE Id_user = %s", (new_password, user_id))
                self.db.connection.commit()
                return True
            else:
                return False