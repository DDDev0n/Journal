from controllers.db_controller import DBController

class ScheduleController:
    def __init__(self):
        self.db = DBController()

    def get_schedule(self):
        return self.db.get_schedule()

    def add_schedule(self, group, date, start_time, end_time, subject, teacher_id):
        return self.db.add_schedule(group, date, start_time, end_time, subject, teacher_id)
