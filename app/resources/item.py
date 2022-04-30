from flask_restful import Resource
from flask import request
from http import HTTPStatus
from app.resources.jwt import *
from app.models.db import db
from app.models.item import Item
from app.models.user import User, MemberItems
from app.models.session import Session

class ItemResource(Resource):
    @jwt_required()
    def patch(self):
        json_data = request.get_json()
        user = User.query.get(get_jwt_identity())
        session = Session.query.get(json_data["session_id"])
        error = None
        if session:
            for item in json_data["updated_items"]:
                item_db = Item.query.get(item["id"])
                if item_db:
                    if user in session.members:
                        if item_db in session.items:
                            if member_item := MemberItems.query.get((user.id, item_db.id)):
                                item_db.amount_brought += (int(item["bring_amount"]) - member_item.item_amount)

                                if item_db.amount_brought < item_db.amount and item_db.amount > item_db.start_amount:
                                    if item["bring_amount"] >= item_db.start_amount:
                                        item_db.amount -= (member_item.item_amount - item["bring_amount"])
                                    else:
                                        item_db.amount = item_db.start_amount

                                if item in json_data["removed_items"]:
                                    db.session.delete(member_item)
                                else:
                                    member_item.item_price = item["price"]
                                    member_item.item_amount = item["bring_amount"]

                            else:
                                member_item = MemberItems(user_id=user.id, item_id=item_db.id, item_amount=item["bring_amount"], session_id=session.id)
                                if "price" in item:
                                    member_item.item_price = item["price"]
                                user.items.append(member_item)
                                item_db.amount_brought += item["bring_amount"]

                            if item_db.amount_brought > item_db.amount:
                                item_db.amount = item_db.amount_brought

                        else:
                            error = {"error": f"{item_db.name} is not part of this session", "status": HTTPStatus.FORBIDDEN}

                    else:
                        error = {"error": "You are not part of this session", "status": HTTPStatus.UNAUTHORIZED}

                else:
                    error = {"error": "Item does not exist (anymore)", "status": HTTPStatus.NOT_FOUND}

                if error:
                    return {"error": error["error"]}, error["status"]

            total_value = 0
            host_costs = 0
            for member_item in session.member_items:
                if member_item.item_price:
                    volume = member_item.item_amount * member_item.item_price
                    total_value += volume
                    if member_item.user_id == session.owner_id:
                        host_costs += volume

            session.total_value = total_value
            session.host_costs = host_costs

            db.session.commit()

            return HTTPStatus.OK

        else:
            return {"error": "Session does not exist anymore"}, HTTPStatus.NOT_FOUND

