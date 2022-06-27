from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from ..models.user import User

class UserSchema(Schema):
    class meta:
        ordered = True

    name = fields.String(required=True)
    email = fields.String(required=True)
    password = fields.String(required=True)

    @validates("name")
    def validate_name(self, name):
        if len(name) < 3:
            raise ValidationError("Name must me at least 3 characters long")
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


class ProfileSchema(Schema):
    class meta:
        ordered = True

    username = fields.String(required=True)
    email = fields.String(required=True)
    promille_record = fields.Float()
    user_id = fields.Integer(required=True)

    @validates("username")
    def validate_username(self, username):
        if len(username) < 3:
            raise ValidationError("Name must me at least 3 characters long")
        elif len(username) > 20:
            raise ValidationError("Name must be 20 or less characters long")

    @validates("email")
    def validate_email(self, email):
        if len(email) > 35:
            raise ValidationError("Email must be 35 or less characters long")

    @validates_schema()
    def validate_name_and_email(self, data, **kwargs):
        if user := User.query.filter_by(username=data["username"]).first():
            if user.id != data["user_id"]:
                raise ValidationError("Name already exists")

        if user := User.query.filter_by(email=data["email"]).first():
            if user.id != data["user_id"]:
                raise ValidationError("Email already exists")

    @validates("promille_record")
    def validate_promille_record(self, promille_record):
        if promille_record < 0.0 or promille_record > 5.0:
            raise ValidationError("Promille record must reach from 0.0 to 5.0")













