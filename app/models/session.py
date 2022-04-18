from .db import db
from .user import User
from .item import Item

class Session(db.Model):
    __tablename__ = "session"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    description = db.Column(db.String(300))
    address = db.Column(db.String(25))
    date = db.Column(db.String(10))
    time = db.Column(db.String(5))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    items = db.relationship("Item", backref="session", lazy=True)

    def get_data(self, user_id=None):
        session_data = {"id": self.id,
                "name": self.name,
                "description": self.description,
                "address": self.address,
                "date": self.date,
                "time": self.time,
                "owner": User.query.get(self.owner_id).get_data(),
                "members": [user.get_data() for user in self.members],
                "invited": [user.get_data() for user in self.invites],
                "items": [item.get_data() for item in self.items],
                "items_by_host": [item.get_data() for item in self.items if item.byHost]}
        if user_id:
            session_data["my_items"] = [item.get_data() for item in User.query.get(user_id).items if Item.query.get(item.item_id) in self.items]

        return session_data