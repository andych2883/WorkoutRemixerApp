from App.database import db

class Workout(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), nullable=False)
  description = db.Column(db.Text, nullable=False)
  type = db.Column(db.String(100), nullable=False)
  body_part = db.Column(db.String(100), nullable=False)
  equipment = db.Column(db.String(100), nullable=False)
  level = db.Column(db.String(100), nullable=False)
  rating = db.Column(db.Float, nullable=False)
  rating_desc = db.Column(db.String(255), nullable=True)
  
  def __init__(self, title, description, type, body_part, equipment, level, rating, rating_desc):
    self.title = title
    self.description = description
    self.type = type
    self.body_part = body_part
    self.equipment = equipment
    self.level = level
    self.rating = rating
    self.rating_desc = rating_desc
  