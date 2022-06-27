from .db import db

class Statistics(db.Model):
    __tablename__ = "statistics"

    id = db.Column(db.Integer(), primary_key=True)
    highest_promille = db.Column(db.String())
    most_sessions_attendet = db.Column(db.String())








