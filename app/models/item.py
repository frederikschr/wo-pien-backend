from .db import db

class Item(db.Model):
    __tablename__ = "item"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    amount = db.Column(db.Integer)
    byHost = db.Column(db.Boolean, default=False)
    session_id = db.Column(db.Integer(), db.ForeignKey("session.id"))

    def get_data(self):
        return {"id": self.id,
                "name": self.name,
                "amount": self.amount,
                "byHost": self.byHost,
                "session_id": self.session_id}
