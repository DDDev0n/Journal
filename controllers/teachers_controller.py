from controllers.db_controller import DBController
class TeachersController:
    def __init__(self):
        self.db = DBController()

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