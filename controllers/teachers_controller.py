from controllers.db_controller import DBController

from PyQt6.QtWidgets import QMessageBox

class TeachersController:
    def __init__(self):
        self.db = DBController()
        self.days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']

    def get_teachers(self):
        return self.db.get_teachers()

    def get_specializations(self):
        return self.db.get_specializations()

    def add_specialization(self, specialization_name):
        self.db.add_specialization(specialization_name)

    def get_teacher_specializations(self, teacher_id):
        return self.db.get_teacher_specializations(teacher_id)

    def add_teacher_specialization(self, teacher_id, specialization_id):
        self.db.add_teacher_specialization(teacher_id, specialization_id)

    def remove_teacher_specialization(self, teacher_id, specialization_id):
        self.db.remove_teacher_specialization(teacher_id, specialization_id)

    def get_specialization_id_by_name(self, specialization_name):
        return self.db.get_specialization_id_by_name(specialization_name)

    def get_teacher_schedule(self, teacher_id):
        if not self.db.is_connected():
            QMessageBox.critical(None, "Database Error", "Database connection not established")
            return []

        try:
            with self.db.connection.cursor() as cursor:
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
                        sch.subj1 = gst.Specialization_id AND gst.Teacher_id = %s

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
                        sch.subj2 = gst.Specialization_id AND gst.Teacher_id = %s

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
                        sch.subj3 = gst.Specialization_id AND gst.Teacher_id = %s

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
                        sch.subj4 = gst.Specialization_id AND gst.Teacher_id = %s

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
                        sch.subj5 = gst.Specialization_id AND gst.Teacher_id = %s
                ) sch ON t.Id_user = sch.Id_teacher
                WHERE t.Id_user = %s
                GROUP BY
                    teacher_name, sch.day
                ORDER BY
                    teacher_name, sch.day;
                """
                cursor.execute(query, (teacher_id, teacher_id, teacher_id, teacher_id, teacher_id, teacher_id))
                rows = cursor.fetchall()
                schedule_data = []
                for row in rows:
                    schedule_data.append(list(row))
                return schedule_data
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Error during DB query: {e}")
            return []