from ..db import db

session_invited_users = db.Table("session_invited_users",
                                 db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
                                 db.Column("session_id", db.Integer, db.ForeignKey("session.id"), primary_key=True))
