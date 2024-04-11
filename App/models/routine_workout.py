from App.database import db

class RoutineWorkout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    routine_id = db.Column(db.Integer, db.ForeignKey('routine.id'), nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    sets = db.Column(db.Integer, nullable=False)

    def __init__(self, routine_id, workout_id, reps, sets):
        self.routine_id = routine_id
        self.workout_id = workout_id
        self.reps = reps
        self.sets = sets
