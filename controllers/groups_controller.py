from controllers.db_controller import DBController

class GroupsController:
    def __init__(self):
        self.db = DBController()

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