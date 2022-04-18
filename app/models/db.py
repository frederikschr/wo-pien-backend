from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
DB_NAME = "database.db"

session_members = db.Table("session_member",
                          db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
                          db.Column("session_id", db.Integer, db.ForeignKey("session.id"), primary_key=True))


session_invites = db.Table("session_invites",
                          db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
                          db.Column("session_id", db.Integer, db.ForeignKey("session.id"), primary_key=True))
