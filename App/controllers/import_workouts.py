from flask import current_app
from App.database import db
from App.models.workout import Workout
import csv

def parse_workouts_from_csv(file_path):
    with current_app.app_context():  # Ensuring access to the Flask app context
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                workout = Workout(
                    title=row['Title'],
                    description=row['Desc'],
                    type=row['Type'],
                    body_part=row['BodyPart'],
                    equipment=row['Equipment'],
                    level=row['Level'],
                    rating=float(row['Rating']),
                    rating_desc=row['RatingDesc']
                )
                db.session.add(workout)
            db.session.commit()


