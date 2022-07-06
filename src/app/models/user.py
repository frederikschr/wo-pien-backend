from .db import db
from .mtm_relationships import session_members, session_invited_users

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(35))
    password = db.Column(db.String())
    avatar_base64 = db.Column(db.String(), default="")
    promille_record = db.Column(db.Float(), default=0.0)
    sessions_attended = db.Column(db.Integer, default=0)
    owned_sessions = db.relationship("Session", backref="owner", lazy=True)
    joined_sessions = db.relationship("Session", secondary=session_members, lazy="subquery", backref=db.backref("members", lazy=True))
    invited_sessions = db.relationship("Session", secondary=session_invited_users, lazy="subquery", backref=db.backref("invited_users", lazy=True))
    is_admin = db.Column(db.Boolean, default=False)
    item_bringings = db.relationship("Member_Item_Bringing", backref=db.backref("bringer"), lazy=True)

    def get_data(self):
        return {"id": self.id,
                "username": self.username,
                "email": self.email,
                "avatar": self.avatar_base64,
                "promille_record": self.promille_record,
                "sessions_attended": self.sessions_attended,
                "is_admin": self.is_admin}









