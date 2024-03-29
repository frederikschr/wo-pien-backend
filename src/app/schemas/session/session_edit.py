from marshmallow import Schema, fields, validates, ValidationError
from ...models.user import User
from ...models.session import Session
from ...models.item import Item

class SessionEditSchema(Schema):
    class Meta:
        ordered = True

    ids = fields.Dict(required=True)
    address = fields.String(required=True)
    coords = fields.Dict(required=False)
    date = fields.String(required=True)
    time = fields.String(required=True)
    members = fields.List(fields.String(), required=True)
    items = fields.List(fields.Dict())
    del_items = fields.List(fields.Dict())

    @validates("ids")
    def validates_ids(self, ids):
        if Session.query.get(ids["session_id"]) == None:
            raise ValidationError("Session does not exist")
        else:
            if Session.query.get(ids["session_id"]).owner_id != ids["user_id"]:
                raise ValidationError("You are not the owner of this session")

    @validates("members")
    def validate_members(self, members):
        for user in members:
            if not User.query.filter_by(username=user).first():
                raise ValidationError(f"User {user} does not exist")

    @validates("items")
    def valdidate_items(self, items):
        for item in items:
            if len(item["name"]) > 20:
                raise ValidationError(f"Item {item['name']} has exceeded the maximal length of 20 characters")

    @validates("del_items")
    def validate_del_items(self, del_items):
        for del_item in del_items:
            del_item = Item.query.get(del_item["id"])
            if not del_item:
                raise ValidationError(f"Item does not exist anymore")

    @validates("address")
    def validate_address(self, address):
        if len(address) < 8:
            raise ValidationError("Address must be at least 8 characters long")
        elif len(address) > 50:
            raise ValidationError("Address must be 50 or less characters long")


