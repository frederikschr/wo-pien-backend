from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from ...models.session import Session
from ...models.item import Item
from ...models.user import User
from ...models.member_item_bringing import Member_Item_Bringing

class ItemBringSchema(Schema):
    class meta:
        ordered = True

    session_id = fields.Integer(required=True)
    user_id = fields.Integer(required=True)
    removed_items = fields.List(fields.Dict())
    new_items = fields.List(fields.Dict())
    updated_items = fields.List(fields.Dict(), required=True)

    def validate_ids(self, data):
        session_id = data["session_id"]
        user_id = data["user_id"]
        session_db = Session.query.get(session_id)
        if not session_db:
            raise ValidationError("Session does not exist (anymore)")
        else:
            user_db = User.query.get(user_id)
            if not user_db in session_db.members:
                raise ValidationError("You are not part of this session_db (anymore)")
            else:
                data["session_db"] = session_db
                data["user_db"] = user_db

    def validate_removed_items(self, data):
        removed_items = data["removed_items"]
        session_db = data["session_db"]
        for removed_item in removed_items:
            if "id" in removed_item:
                item_db = Item.query.get(removed_item["id"])
                if item_db:
                    if item_db in session_db.items:
                        if not Member_Item_Bringing.query.get((data["user_id"], item_db.id)):
                            raise ValidationError(f"Bringing for item {item_db.name} does not exist")

                        else:
                            removed_item["item_db"] = item_db

                    else:
                        raise ValidationError(f"{item_db.name} is not part of {session_db.name}")

                else:
                    raise ValidationError("Item does not exist (anymore)")

            else:
                raise ValidationError("Items must contain ID")

    def validate_updated_items(self, data):
        updated_items = data["updated_items"]
        session_db = data["session_db"]
        for updated_item in updated_items:
            if "id" in updated_item:
                item_db = Item.query.get(updated_item["id"])
                if item_db:
                    if item_db in session_db.items:
                        if updated_item["bring_amount"] != "":
                            if updated_item["bring_amount"] < 1 or updated_item["bring_amount"] > 1000:
                                raise ValidationError("Bring amount must reach from 0 to 1000")

                            else:
                                if "price" in updated_item:
                                    if updated_item["price"] < 0 or updated_item["price"] > 1000:
                                        raise ValidationError("Price must reach from 0 to 1000")

                            updated_item["item_db"] = item_db

                        else:
                            raise ValidationError(f"Amount for item {item_db.name} can't be empty")
                    else:
                        raise ValidationError(f"{item_db.name} is not part of {session_db.name}")

                else:
                    raise ValidationError("Item does not exist (anymore)")

            else:
                raise ValidationError("Items must contain ID")

    def validate_new_items(self, data):
        new_items = data["new_items"]
        session_db = data["session_db"]
        for new_item in new_items:
            item_db = Item.query.filter_by(name=new_item["name"]).first()
            if not item_db:
                if new_item["amount"] > 1000 or new_item["amount"] < 1:
                    raise ValidationError("Amount must reach from 1 to 1000")
            else:
                if item_db in session_db.items:
                    raise ValidationError(f"Item {new_item['name']} already exists")

    @validates_schema
    def validate_data(self, data, **kwargs):
        try:
            self.validate_ids(data)
            self.validate_removed_items(data)
            self.validate_updated_items(data)
            self.validate_new_items(data)

        except ValidationError as e:
            raise e
