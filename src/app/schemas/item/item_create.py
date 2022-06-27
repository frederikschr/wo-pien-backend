from marshmallow import Schema, fields, validates, ValidationError

class ItemCreateSchema(Schema):
    class meta:
        ordered = True

    name = fields.String(required=True)
    amount = fields.Integer(required=True)
    byHost = fields.Bool(required=True)

    @validates("name")
    def validate_name(self, name):
        if len(name) > 20 or len(name) < 1:
            raise ValidationError("Item names must reach from 1 to 20 characters")

    @validates("amount")
    def validate_amount(self, amount):
        if amount < 1 or amount > 1000:
            raise ValidationError("Amount must be between 1 and 1000")

