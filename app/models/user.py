from .db import db, session_members, session_invites

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(35))
    password = db.Column(db.String(20))
    owned_sessions = db.relationship("Session", backref="owner", lazy=True)
    sessions = db.relationship("Session", secondary=session_members, lazy="subquery", backref=db.backref("members", lazy=True))
    invited_sessions = db.relationship("Session", secondary=session_invites, lazy="subquery", backref=db.backref("invites", lazy=True))
    is_admin = db.Column(db.Boolean, default=False)

    def get_data(self):
        return {"id": self.id,
                "username": self.username,
                "email": self.email}








