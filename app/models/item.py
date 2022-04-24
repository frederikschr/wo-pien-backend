from .db import db

class Item(db.Model):
    __tablename__ = "item"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    amount = db.Column(db.Integer)
    start_amount = db.Column(db.Integer)
    amount_brought = db.Column(db.Integer, default=0)
    byHost = db.Column(db.Boolean, default=False)
    session_id = db.Column(db.Integer(), db.ForeignKey("session.id"))
    bringings = db.relationship("MemberItems", backref="item", lazy=True)

    def get_data(self):
        return {"id": self.id,
                "name": self.name,
                "amount": self.amount,
                "start_amount": self.start_amount,
                "amount_brought": self.amount_brought,
                "byHost": self.byHost,
                "session_id": self.session_id}
