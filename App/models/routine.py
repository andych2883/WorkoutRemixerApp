from App.database import db

class Routine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    routine_workouts = db.relationship('RoutineWorkout', backref='routine', lazy=True)

    def __init__(self, title, user_id):
        self.title = title
        self.user_id = user_id