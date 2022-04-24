from flask_restful import Resource
from flask import request
from marshmallow import ValidationError
from http import HTTPStatus
from app.resources.jwt import *
from app.models.session import *
from app.models.user import User, MemberItems
from app.models.item import Item
from app.schemas.session.session import SessionSchema
from app.schemas.session.session_edit import SessionEditSchema

class SessionResource(Resource):
    @jwt_required()
    def post(self):
        json_data = request.get_json()
        sessionSchema = SessionSchema()
        try:
            session_data = sessionSchema.load(data=json_data)
            owner = User.query.get(get_jwt_identity())
            session = Session(name=session_data["name"], description=session_data["description"],
                              address=session_data["address"], date=session_data["date"],
                              time=session_data["time"], owner_id=owner.id)

            for member in session_data["members"]:
                user = User.query.filter_by(username=member).first()
                if not user.id == session.owner_id:
                    session.invites.append(user)
                else:
                    session.members.append(user)

            for item in session_data["items"]:
                session.items.append(Item(name=item["name"], amount=item["amount"], byHost=item["byHost"], start_amount=item["amount"]))

            db.session.add(session)
            db.session.commit()

            for item in session.items:
                if item.byHost:
                    host_item = MemberItems(user_id=owner.id, item_id=item.id, item_amount=item.amount, session_id=session.id)
                    owner.items.append(host_item)
                    item.amount_brought = host_item.item_amount

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
            return {"session": Session.query.get(int(id)).get_data(user_id=get_jwt_identity())}, HTTPStatus.OK
        return {"sessions": [session.get_data() for session in User.query.get(get_jwt_identity()).sessions],
                "invited_sessions": [session.get_data() for session in User.query.get(get_jwt_identity()).invited_sessions]}, HTTPStatus.OK


class SessionEditResource(Resource):
    @jwt_required()
    def patch(self):
        json_data = request.get_json()
        user = User.query.get(get_jwt_identity())
        session_edit_schema = SessionEditSchema()
        try:
            json_data["ids"]["user_id"] = get_jwt_identity()
            edited_session_data = session_edit_schema.load(data=json_data)
            session = Session.query.get(edited_session_data["ids"]["session_id"])

            session.address = edited_session_data["address"]
            session.date = edited_session_data["date"]
            session.time = edited_session_data["time"]

            for member in session.members:
                if not member.username in edited_session_data["members"] and member.id != session.owner_id:
                    print(f"removed {member.username}")
                    session.members.remove(member)

            for member in edited_session_data["members"]:
                member = User.query.filter_by(username=member).first()
                if not member in session.members:
                    session.members.append(member)

            for item in session.items:
                if item not in edited_session_data["items"]:
                    session.items.remove(item)

            db.session.commit()

            return {"message": "Successfully edited session"}, HTTPStatus.OK

        except ValidationError as e:
            print(e.messages)



