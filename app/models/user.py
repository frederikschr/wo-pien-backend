from .db import db, session_members, session_invites
from .item import Item

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(35))
    password = db.Column(db.String(80))
    owned_sessions = db.relationship("Session", backref="owner", lazy=True)
    sessions = db.relationship("Session", secondary=session_members, lazy="subquery", backref=db.backref("members", lazy=True))
    invited_sessions = db.relationship("Session", secondary=session_invites, lazy="subquery", backref=db.backref("invites", lazy=True))
    is_admin = db.Column(db.Boolean, default=False)
    items = db.relationship("MemberItems")

    def get_data(self):
        return {"id": self.id,
                "username": self.username,
                "email": self.email}

class MemberItems(db.Model):
    __tablename__ = "member_items"

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("session.id"))
    item_amount = db.Column(db.Integer)
    item_price = db.Column(db.Float)

    def get_data(self):
        member_items_data = {
            "user": User.query.get(self.user_id).get_data(),
            "bring_amount": self.item_amount,
            "price": self.item_price
        }
        item_data = Item.query.get(self.item_id).get_data()
        member_items_data.update(item_data)
        return member_items_data









