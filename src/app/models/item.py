from .db import db

class Item(db.Model):
    __tablename__ = "item"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    amount_needed = db.Column(db.Integer)
    default_needed_amount = db.Column(db.Integer)
    amount_brought = db.Column(db.Integer, default=0)
    byHost = db.Column(db.Boolean, default=False)
    session_id = db.Column(db.Integer(), db.ForeignKey("session.id"))
    bringings = db.relationship("Member_Item_Bringing", backref="item", lazy=True)

    def get_data(self):
        return {"id": self.id,
                "name": self.name,
                "amount": self.amount_needed,
                "start_amount": self.default_needed_amount,
                "amount_brought": self.amount_brought,
                "byHost": self.byHost,
                "session_id": self.session_id}
