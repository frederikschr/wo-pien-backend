from .db import db
from .user import User
from .item import Item

class Session(db.Model):
    __tablename__ = "session"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    description = db.Column(db.String(300))
    address = db.Column(db.String(25))
    coords = db.Column(db.JSON(), default={"lat": 51.9, "lng": 7.6})
    date = db.Column(db.String(10))
    time = db.Column(db.String(5))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    total_value = db.Column(db.Integer)
    host_costs = db.Column(db.Integer)
    items = db.relationship("Item", backref="session", lazy=True)
    item_member_bringings = db.relationship("Member_Item_Bringing", backref="session", lazy=True)
    bringings = db.Column(db.JSON, default=[])

    def get_data(self, user_id=None):
        session_data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "address": self.address,
            "coords": self.coords,
            "date": self.date,
            "time": self.time,
            "owner": self.owner.get_data(),
            "members": [user.get_data() for user in self.members],
            "invited": [user.get_data() for user in self.invited_users],
            "items": [item.get_data() for item in self.items],
            "items_by_host": [item.get_data() for item in self.items if item.byHost],
            "host_costs": self.host_costs,
            "total_value": self.total_value,
            "member_items": self.bringings}

        if user_id:
            session_data["my_items"] = [item.get_data() for item in User.query.get(user_id).item_bringings if Item.query.get(item.item_id) in self.items]
            my_costs = 0
            for item in session_data["my_items"]:
                if item["price"]:
                    my_costs += item["bring_amount"] * item["price"]
            session_data["my_costs"] = my_costs

        return session_data