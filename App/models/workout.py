from App.database import db

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(50), nullable=False)
    body_part = db.Column(db.String(50), nullable=False)
    equipment = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(50), nullable=False)
    routines = db.relationship('RoutineWorkout', backref='workout', lazy=True)

def __init__(self, title, description, type, body_part, equipment, level, rating, rating_description):
    self.title = title
    self.description = description
    self.type = type
    self.body_part = body_part
    self.equipment = equipment
    self.level = level
