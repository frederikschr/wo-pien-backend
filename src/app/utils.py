import time
import datetime as dt
from .models.db import db
from .models.item import Item
from .models.user import User

def check_sessions(user):
    today = time.strptime(str(dt.date.today()), "%Y-%m-%d")
    for session in user.sessions:
        if time.strptime(session.date, "%Y-%m-%d") < today:
            del_all_associates_session(session)
            for member in session.members:
                member.sessions_attended += 1
            db.session.commit()

def del_all_associates_user(user, session):
    session_items = [item.id for item in session.items]
    for bringing in user.items:
        if bringing.item_id in session_items:
            item = Item.query.get(bringing.item_id)
            item.amount_brought -= bringing.item_amount
            db.session.delete(bringing)
    db.session.commit()

def del_all_associates_session(session):
    for bringing in session.member_items:
        db.session.delete(bringing)
    for item in session.items:
        db.session.delete(item)
    db.session.commit()

def member_items_to_dict(session):
    user_costs = {}
    for user in session.members:
        if user.username not in user_costs.keys():
            user_costs[user.username] = 0
    member_items = session.member_items
    for bringing in member_items:
        user = User.query.get(bringing.user_id)
        user_costs[user.username] += bringing.item_amount * bringing.item_price
    return user_costs







