from .db import db

class Member_Item_Bringing(db.Model):
    __tablename__ = "member_item_bringing"

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("session.id"))
    item_amount = db.Column(db.Integer)
    item_price = db.Column(db.Float, default=1.0)

    def get_data(self):
        member_items_data = {
            "user": self.bringer.get_data(),
            "bring_amount": self.item_amount,
            "price": self.item_price
        }
        item_data = self.item.get_data()
        member_items_data.update(item_data)
        return member_items_data
