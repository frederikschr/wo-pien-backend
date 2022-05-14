import base64
from flask_restful import Resource
from flask import request
from http import HTTPStatus
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import ValidationError
from .jwt import *
import datetime as dt
from app.models.user import *
from app.schemas.user import UserSchema, ProfileSchema
import time

def check_sessions(user):
    today = time.strptime(str(dt.date.today()), "%Y-%m-%d")
    for session in user.sessions:
        if time.strptime(session.date, "%Y-%m-%d") < today:
            for bringing in session.member_items:
                db.session.delete(bringing)

            for item in session.items:
                db.session.delete(item)

            db.session.delete(session)
            db.session.commit()

class UserResource(Resource):
    def post(self):
        json_data = request.get_json()
        userSchema = UserSchema()
        try:
            user_data = userSchema.load(data=json_data)
            user = User(username=user_data["name"], email=user_data["email"], password=generate_password_hash(user_data["password"], "sha256"))
            db.session.add(user)
            db.session.commit()
            return {"message": f"Successfully created {user.username}"}, HTTPStatus.CREATED
        except ValidationError as e:
            return e.messages, HTTPStatus.BAD_REQUEST

    def get(self):
        username = request.args.get("name")
        password = request.args.get("password")

        user = User.query.filter_by(username=username).first()

        if user:
            if check_password_hash(user.password, password):
                expires = dt.timedelta(hours=3)
                access_token = create_access_token(identity=user.id, expires_delta=expires, fresh=True)

                check_sessions(user)

                return {"user": user.get_data(), "token": access_token, "all_users": [user.username for user in User.query.all()]}, HTTPStatus.OK
            else:
                data = {"error": "Incorrect password", "status": HTTPStatus.FORBIDDEN}
        else:
            data = {"error": "User does not exist", "status": HTTPStatus.NOT_FOUND}

        return {"error": data["error"]}, data["status"]


class ProfileResource(Resource):
    @jwt_required()
    def post(self):
        user = User.query.get(get_jwt_identity())
        json_data = request.get_json()
        profileSchema = ProfileSchema()
        try:
            json_data["user_id"] = user.id
            profile_data = profileSchema.load(data=json_data)

            user.username = profile_data["username"]
            user.email = profile_data["email"]
            user.promille_record = profile_data["promille_record"]

            db.session.commit()

            return {"message": "Successfully updated profile"}, HTTPStatus.OK

        except ValidationError as e:
            return e.messages, HTTPStatus.BAD_REQUEST

    @jwt_required()
    def get(self):
        return {"user": User.query.get(get_jwt_identity()).get_data()}, HTTPStatus.OK


class AvatarResource(Resource):
    @jwt_required()
    def post(self):
        file = request.files["file"]

        print(file)

        if file:
            user = User.query.get(get_jwt_identity())
            file_data = file.read()
            user.avatar_base64 = base64.b64encode(file_data).decode("ascii")
            db.session.commit()

            return {"message": "Successfully uploaded avatar"}, HTTPStatus.OK

        else:
            return {"error": "File is missing"}, HTTPStatus.NOT_FOUND













