from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from app.models.session import Session
from app.models.item import Item
from app.models.user import MemberItems, User

class ItemBringSchema(Schema):
    class meta:
        ordered = True

    session_id = fields.Integer(required=True)
    user_id = fields.Integer(required=True)
    removed_items = fields.List(fields.Dict())
    new_items = fields.List(fields.Dict())
    updated_items = fields.List(fields.Dict(), required=True)

    @validates("session_id")
    def validate_session_id(self, session_id):
        session = Session.query.get(session_id)
        if not session:
            raise ValidationError("Session does not exist (anymore)")

    @validates_schema()
    def validate_items(self, data, **kwargs):
        if session := Session.query.get(data["session_id"]):
            if User.query.get(data["user_id"]) in session.members:

                for removed_item in data["removed_items"]:
                    if "id" in removed_item:
                        item_db = Item.query.get(removed_item["id"])
                        if item_db:
                            if item_db in session.items:
                                if not MemberItems.query.get((data["user_id"], item_db.id)):
                                    raise ValidationError(f"Bringing for item {item_db.name} does not exist")
                            else:
                                raise ValidationError(f"{item_db.name} is not part of {session.name}")

                        else:
                            raise ValidationError("Item does not exist (anymore)")

                    else:
                        raise ValidationError("Items must contain ID")

                for updated_item in data["updated_items"]:
                    if "id" in updated_item:
                        item_db = Item.query.get(updated_item["id"])
                        if item_db:
                            if item_db in session.items:
                                if updated_item["bring_amount"] != "":
                                    if updated_item["bring_amount"] < 1 or updated_item["bring_amount"] > 1000:
                                        raise ValidationError("Bring amount must reach from 0 to 1000")
                                else:
                                    raise ValidationError(f"Amount for item {item_db.name} can't be empty")
                            else:
                                raise ValidationError(f"{item_db.name} is not part of {session.name}")

                        else:
                            raise ValidationError("Item does not exist (anymore)")

                    else:
                        raise ValidationError("Items must contain ID")

                for new_item in data["new_items"]:
                    item_db = Item.query.filter_by(name=new_item["name"]).first()
                    if not item_db:
                        if new_item["amount"] > 1000 or new_item["amount"] < 1:
                            raise ValidationError("Amount must reach from 1 to 1000")

                    else:
                        if item_db in session.items:
                            raise ValidationError(f"Item {new_item['name']} already exists")
            else:
                raise ValidationError("You have been removed from this session")


