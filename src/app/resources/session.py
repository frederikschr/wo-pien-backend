from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from http import HTTPStatus
from ..models.session import *
from ..models.user import User
from ..models.member_item_bringing import Member_Item_Bringing
from ..models.item import Item
from ..schemas.session.session_create import SessionSchema
from ..schemas.session.session_edit import SessionEditSchema
from ..schemas.item.item_create import ItemCreateSchema
from ..utils import del_all_associates_user, member_items_to_dict

class SessionResource(Resource):
    @jwt_required()
    def post(self):
        json_data = request.get_json()
        sessionSchema = SessionSchema()
        item_create_schema = ItemCreateSchema()
        try:
            session_data = sessionSchema.load(data=json_data)
            owner = User.query.get(get_jwt_identity())
            session = Session(name=session_data["name"], description=session_data["description"],
                              address=session_data["address"], coords=session_data["coords"], date=session_data["date"],
                              time=session_data["time"], owner_id=owner.id)

            for member_name in session_data["members"]:
                user = User.query.filter_by(username=member_name).first()
                if not user.id == session.owner_id:
                    session.invited_users.append(user)
                else:
                    session.members.append(user)

            for item in session_data["items"]:
                try:
                    item_data = item_create_schema.load(data=item)
                    session.items.append(Item(name=item_data["name"], amount_needed=item_data["amount"], byHost=item_data["byHost"], default_needed_amount=item_data["amount"]))
                except ValidationError as e:
                    return e.messages, HTTPStatus.BAD_REQUEST

            db.session.add(session)
            db.session.commit()

            for item in session.items:
                if item.byHost:
                    host_item = Member_Item_Bringing(user_id=owner.id, item_id=item.id, item_amount=item.amount_needed, session_id=session.id)
                    owner.item_bringings.append(host_item)
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
        if session:
            if session in user.invited_sessions:
                user.invited_sessions.remove(session)
                if json_data["accepted"]:
                    user.joined_sessions.append(session)
                    message = {"message": f"You successfully joined {session.name}"}
                else:
                    message = {"message": f"You successfully rejected {session.name}"}

                session.bringings = member_items_to_dict(session)

                db.session.commit()
                return message, HTTPStatus.OK

            else:
                if not session.owner_id == user.id:
                    session.members.remove(user)
                    db.session.commit()
                    del_all_associates_user(user, session)
                    session.bringings = member_items_to_dict(session)
                    return {"message": f"You successfully left {session.name}"}, HTTPStatus.OK

                else:
                    error = "Owner can not leave the session"
        else:
            error = "Session does not exist (anymore)"

        return {"error": [error]}, HTTPStatus.BAD_REQUEST

    @jwt_required()
    def get(self):
        if id := request.args.get("id"):
            if Session.query.get(id):
                return {"session": Session.query.get(int(id)).get_data(user_id=get_jwt_identity())}, HTTPStatus.OK
            return {"error": "Session does not exist (anymore)"}, HTTPStatus.NOT_FOUND

        return {"sessions": [session.get_data() for session in User.query.get(get_jwt_identity()).joined_sessions],
                "invited_sessions": [session.get_data() for session in User.query.get(get_jwt_identity()).invited_sessions]}, HTTPStatus.OK

class SessionEditResource(Resource):
    @jwt_required()
    def patch(self):
        json_data = request.get_json()

        print(json_data)

        session_edit_schema = SessionEditSchema()
        item_create_schema = ItemCreateSchema()
        try:
            json_data["ids"]["user_id"] = get_jwt_identity()
            edited_session_data = session_edit_schema.load(data=json_data)
            session = Session.query.get(edited_session_data["ids"]["session_id"])

            print(edited_session_data)

            session.address = edited_session_data["address"]
            session.coords = edited_session_data["coords"]
            session.date = edited_session_data["date"]
            session.time = edited_session_data["time"]

            for member in session.members:
                if not member.username in edited_session_data["members"] and member.id != session.owner_id:
                    session.members.remove(member)
                    del_all_associates_user(member, session)

            for member in edited_session_data["members"]:
                member = User.query.filter_by(username=member).first()
                if not member in session.members:
                    session.invited_users.append(member)

            for updated_item in edited_session_data["items"]:
                if "id" in updated_item:
                    for item in session.items:
                        if item.id == updated_item["id"]:
                            if updated_item["amount"] > 0 and updated_item["amount"] < 1000:
                                item.start_amount = updated_item["amount"]
                                item.amount = updated_item["amount"]
                                break
                            else:
                                return {'amount': ['Amount must be between 1 and 1000']}, HTTPStatus.BAD_REQUEST

                else:
                    try:
                        item_data = item_create_schema.load(data=updated_item)
                        session.items.append(
                            Item(name=item_data["name"], amount_needed=item_data["amount"], byHost=item_data["byHost"],
                                 default_needed_amount=item_data["amount"]))

                    except ValidationError as e:
                        return e.messages, HTTPStatus.BAD_REQUEST

            if "del_items" in edited_session_data:
                for del_item in edited_session_data["del_items"]:
                    item = Item.query.get(del_item["id"])
                    for bringing in item.bringings:
                        db.session.delete(bringing)

                    db.session.delete(item)

            db.session.commit()

            return {"message": "Successfully edited session"}, HTTPStatus.OK

        except ValidationError as e:
            return e.messages, HTTPStatus.BAD_REQUEST

    @jwt_required()
    def delete(self):
        json_data = request.get_json()
        user = User.query.get(get_jwt_identity())
        if "session_id" in json_data:
            session = Session.query.get(json_data["session_id"])
            if session:
                if session.owner_id == user.id:

                    for bringing in session.item_member_bringings:
                        db.session.delete(bringing)

                    for item in session.items:
                        db.session.delete(item)

                    db.session.delete(session)
                    db.session.commit()

                    return {"message": f"Successfully deleted {session.name}"}, HTTPStatus.OK

                else:
                    error = {"message": "You are not the owner of this session", "status": HTTPStatus.UNAUTHORIZED}

            else:
                error = {"message": "Session does not exist", "status": HTTPStatus.BAD_REQUEST}

        else:
            error = {"message": "Missing session_id in request body", "status": HTTPStatus.BAD_REQUEST}

        return {"error": error["error"]}, error["status"]



