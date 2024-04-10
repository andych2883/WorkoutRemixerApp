from App.database import db

class RoutineWorkout(db.Model):
  routine_id = db.Column(db.Integer, db.ForeignKey('routine.id'), primary_key=True)
  workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), primary_key=True)
  workout = db.relationship('Workout')
  