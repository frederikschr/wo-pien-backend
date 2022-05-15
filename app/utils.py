import time
import datetime as dt
from app.models.db import db

def check_sessions(user):
    today = time.strptime(str(dt.date.today()), "%Y-%m-%d")
    for session in user.sessions:
        if time.strptime(session.date, "%Y-%m-%d") < today:
            for bringing in session.member_items:
                db.session.delete(bringing)

            for item in session.items:
                db.session.delete(item)

            for member in session.members:
                member.sessions_attended += 1

            db.session.delete(session)
            db.session.commit()

