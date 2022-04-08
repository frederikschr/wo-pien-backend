from flask_restful import Resource
from flask import request
from marshmallow import ValidationError
from http import HTTPStatus
from app.resources.jwt import *
from app.models.session import *
from app.models.user import User
from app.models.item import Item
from app.schemas.session import SessionSchema

class SessionResource(Resource):
    @jwt_required()
    def post(self):
        json_data = request.get_json()
        sessionSchema = SessionSchema()
        try:
            session_data = sessionSchema.load(data=json_data)
            user = User.query.get(get_jwt_identity())
            session = Session(name=session_data["name"], description=session_data["description"],
                              address=session_data["address"], date=session_data["date"],
                              time=session_data["time"], owner_id=user.id)

            for member in session_data["members"]:
                user = User.query.filter_by(username=member).first()
                if not user.id == session.owner_id:
                    session.invites.append(user)
                else:
                    session.members.append(user)

            for item in session_data["items"]:
                session.items.append(Item(name=item["name"], amount=item["amount"], byHost=item["byHost"]))

            db.session.add(session)
            db.session.commit()
            return HTTPStatus.CREATED

        except ValidationError as e:
            return e.messages, HTTPStatus.BAD_REQUEST


    @jwt_required()
    def patch(self):
        json_data = request.get_json()
        user = User.query.get(get_jwt_identity())
        session = Session.query.get(json_data["session"])
        if json_data["accepted"]:
            user.sessions.append(session)
        user.invited_sessions.remove(session)
        db.session.commit()
        return {"message": f"You successfully joined {session.name}"} if json_data["accepted"] \
                   else {"message": f"You successfully rejected {session.name}"}, HTTPStatus.OK

    @jwt_required()
    def get(self):
        if id := request.args.get("id"):
            return {"session": Session.query.get(int(id)).get_data()}, HTTPStatus.OK
        return {"sessions": [session.get_data() for session in User.query.get(get_jwt_identity()).sessions],
                "invited_sessions": [session.get_data() for session in User.query.get(get_jwt_identity()).invited_sessions]}, HTTPStatus.OK




