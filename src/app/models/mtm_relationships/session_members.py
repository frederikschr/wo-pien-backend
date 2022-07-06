from ..db import db

session_members = db.Table("session_members",
                          db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
                          db.Column("session_id", db.Integer, db.ForeignKey("session.id"), primary_key=True))
