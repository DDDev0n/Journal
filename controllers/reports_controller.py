from PyQt6.QtWidgets import QMessageBox

class ReportsController:
    def __init__(self, connection):
        self.connection = connection

    def get_all_teacher_schedules(self):
        if not self.connection:
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return []

        try:
            with self.connection.cursor() as cursor:
                query = """
                SELECT
                    CONCAT(t.Name, ' ', t.Surname) AS teacher_name,
                    sch.day,
                    MAX(CASE WHEN sch.period = 1 THEN CONCAT(sch.subject, ' - ', sch.Group_name) ELSE '' END) AS period_1,
                    MAX(CASE WHEN sch.period = 2 THEN CONCAT(sch.subject, ' - ', sch.Group_name) ELSE '' END) AS period_2,
                    MAX(CASE WHEN sch.period = 3 THEN CONCAT(sch.subject, ' - ', sch.Group_name) ELSE '' END) AS period_3,
                    MAX(CASE WHEN sch.period = 4 THEN CONCAT(sch.subject, ' - ', sch.Group_name) ELSE '' END) AS period_4,
                    MAX(CASE WHEN sch.period = 5 THEN CONCAT(sch.subject, ' - ', sch.Group_name) ELSE '' END) AS period_5
                FROM
                    Teacher t
                JOIN (
                    SELECT
                        gst.Teacher_id AS Id_teacher,
                        sch.day,
                        1 AS period,
                        sp1.Specialization_name AS subject,
                        grp.Group_name
                    FROM
                        Schedule sch
                    JOIN
                        Groups_Specialization_teacher gst ON sch.Id_group = gst.Group_id
                    JOIN
                        Specializations sp1 ON sch.subj1 = sp1.Id_specialization
                    JOIN
                        `Groups` grp ON sch.Id_group = grp.Id_group
                    WHERE
                        sch.subj1 = gst.Specialization_id

                    UNION ALL

                    SELECT
                        gst.Teacher_id AS Id_teacher,
                        sch.day,
                        2 AS period,
                        sp2.Specialization_name AS subject,
                        grp.Group_name
                    FROM
                        Schedule sch
                    JOIN
                        Groups_Specialization_teacher gst ON sch.Id_group = gst.Group_id
                    JOIN
                        Specializations sp2 ON sch.subj2 = sp2.Id_specialization
                    JOIN
                        `Groups` grp ON sch.Id_group = grp.Id_group
                    WHERE
                        sch.subj2 = gst.Specialization_id

                    UNION ALL

                    SELECT
                        gst.Teacher_id AS Id_teacher,
                        sch.day,
                        3 AS period,
                        sp3.Specialization_name AS subject,
                        grp.Group_name
                    FROM
                        Schedule sch
                    JOIN
                        Groups_Specialization_teacher gst ON sch.Id_group = gst.Group_id
                    JOIN
                        Specializations sp3 ON sch.subj3 = sp3.Id_specialization
                    JOIN
                        `Groups` grp ON sch.Id_group = grp.Id_group
                    WHERE
                        sch.subj3 = gst.Specialization_id

                    UNION ALL

                    SELECT
                        gst.Teacher_id AS Id_teacher,
                        sch.day,
                        4 AS period,
                        sp4.Specialization_name AS subject,
                        grp.Group_name
                    FROM
                        Schedule sch
                    JOIN
                        Groups_Specialization_teacher gst ON sch.Id_group = gst.Group_id
                    JOIN
                        Specializations sp4 ON sch.subj4 = sp4.Id_specialization
                    JOIN
                        `Groups` grp ON sch.Id_group = grp.Id_group
                    WHERE
                        sch.subj4 = gst.Specialization_id

                    UNION ALL

                    SELECT
                        gst.Teacher_id AS Id_teacher,
                        sch.day,
                        5 AS period,
                        sp5.Specialization_name AS subject,
                        grp.Group_name
                    FROM
                        Schedule sch
                    JOIN
                        Groups_Specialization_teacher gst ON sch.Id_group = gst.Group_id
                    JOIN
                        Specializations sp5 ON sch.subj5 = sp5.Id_specialization
                    JOIN
                        `Groups` grp ON sch.Id_group = grp.Id_group
                    WHERE
                        sch.subj5 = gst.Specialization_id
                ) sch ON t.Id_user = sch.Id_teacher
                GROUP BY
                    teacher_name, sch.day
                ORDER BY
                    teacher_name, sch.day;
                """
                cursor.execute(query)
                schedules = cursor.fetchall()

                all_schedules = []
                for schedule in schedules:
                    all_schedules.append(schedule)

                return all_schedules
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return []

    def get_all_group_schedules(self):
        try:
            with self.connection.cursor() as cursor:
                query = """
                SELECT
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
                ORDER BY
                    grp.Group_name, sch.day
                """
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return []

    def get_inactive_teachers(self):
        query = """
        SELECT CONCAT(Name, ' ', Surname) AS full_name, Login, CreateCode AS activation_code
        FROM Users
        JOIN Teacher ON Users.Id_user = Teacher.Id_user
        WHERE Users.Id_role = (SELECT Id_role FROM Roles WHERE Name = 'teacher') AND Users.Pas IS NULL
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def get_inactive_students(self):
        query = """
        SELECT CONCAT(Name, ' ', Surname) AS full_name, Login, Group_name, CreateCode AS activation_code
        FROM Users
        JOIN Student ON Users.Id_user = Student.Id_user
        JOIN `Groups` ON Student.Id_group = `Groups`.Id_group
        WHERE Users.Id_role = (SELECT Id_role FROM Roles WHERE Name = 'student') AND Users.Pas IS NULL
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()