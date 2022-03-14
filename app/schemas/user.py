from marshmallow import Schema, fields, validates, ValidationError
from app.models.user import User

class UserSchema(Schema):
    class meta:
        ordered = True

    name = fields.String(required=True)
    email = fields.String(required=True)
    password = fields.String(required=True)

    @validates("name")
    def validate_name(self, name):
        if len(name) < 6:
            raise ValidationError("Name must me at least 6 characters long")
        elif len(name) > 20:
            raise ValidationError("Name must be 20 or less characters long")
        elif User.query.filter_by(username=name).first():
            raise ValidationError("Name already exists")

    @validates("email")
    def validate_email(self, email):
        if len(email) > 35:
            raise ValidationError("Email must be 35 or less characters long")
        elif User.query.filter_by(email=email).first():
            raise ValidationError("Email already used")

    @validates("password")
    def validate_password(self, password):
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        elif len(password) > 20:
            raise ValidationError("Password must be 20 or less characters long")














