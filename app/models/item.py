from .db import db

class Item(db.Model):
    __tablename__ = "item"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    amount = db.Column(db.Integer)
    price = db.Column(db.Integer)
    amount_brought = db.Column(db.Integer, default=0)
    byHost = db.Column(db.Boolean, default=False)
    session_id = db.Column(db.Integer(), db.ForeignKey("session.id"))

    def get_data(self):
        return {"id": self.id,
                "name": self.name,
                "amount": self.amount,
                "price": self.price,
                "amount_brought": self.amount_brought,
                "byHost": self.byHost,
                "session_id": self.session_id}
