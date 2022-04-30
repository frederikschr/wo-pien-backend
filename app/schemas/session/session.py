from marshmallow import Schema, fields, validates, ValidationError
from app.models.user import User

class SessionSchema(Schema):
    class Meta:
        ordered = True

    name = fields.String(required=True)
    description = fields.String(required=False)
    address = fields.String(required=True)
    date = fields.String(required=True)
    time = fields.String(required=True)
    members = fields.List(fields.String(), required=True)
    items = fields.List(fields.Dict())

    @validates("name")
    def validate_name(self, name):
        if len(name) < 6:
            raise ValidationError("Name must me at least 6 characters long")
        elif len(name) > 30:
            raise ValidationError("Name must be 30 or less characters long")

    @validates("description")
    def validate_description(self, description):
        if len(description) > 300:
            raise ValidationError("Description must be 300 or less characters long")

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

    @validates("address")
    def validate_address(self, address):
        if len(address) < 8:
            raise ValidationError("Address must be at least 8 characters long")
        elif len(address) > 35:
            raise ValidationError("Address must be 25 or less characters long")

