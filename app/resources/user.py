from flask_restful import Resource
from flask import request
from http import HTTPStatus
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import ValidationError
from .jwt import *
import datetime as dt
from app.models.user import *
from app.schemas.user import UserSchema
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

                return {"user": user.get_data(), "token": access_token}, HTTPStatus.OK
            else:
                data = {"error": "Incorrect password", "status": HTTPStatus.FORBIDDEN}
        else:
            data = {"error": "User does not exist", "status": HTTPStatus.NOT_FOUND}

        return {"error": data["error"]}, data["status"]







