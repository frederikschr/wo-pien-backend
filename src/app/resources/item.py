from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from http import HTTPStatus
from marshmallow import ValidationError
from ..models.db import db
from ..models.item import Item
from ..models.user import User
from ..models.member_item_bringing import Member_Item_Bringing
from ..schemas.item.item_bring import ItemBringSchema
from ..utils import calculate_session_metrics

class ItemBringResource(Resource):
    @jwt_required()
    def patch(self):
        json_data = request.get_json()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        json_data["user_id"] = user_id
        item_bring_schema = ItemBringSchema()
        try:
            item_bring_data = item_bring_schema.load(data=json_data)

            session = item_bring_data["session_db"]

            for item in item_bring_data["removed_items"]:
                item_db = item["item_db"]
                member_item = Member_Item_Bringing.query.get((user.id, item_db.id))
                db.session.delete(member_item)
                item_db.amount_brought -= item["bring_amount"]

            for item in item_bring_data["updated_items"]:

                item_db = item["item_db"]
                member_item = Member_Item_Bringing.query.get((user.id, item_db.id))

                if member_item:

                    item_db.amount_brought += (int(item["bring_amount"]) - member_item.item_amount)

                    if item_db.amount_brought < item_db.amount_needed and item_db.amount_needed > item_db.default_needed_amount:
                        if item["bring_amount"] >= item_db.default_needed_amount:
                            item_db.amount_needed -= (member_item.item_amount - item["bring_amount"])
                        else:
                            item_db.amount_needed = item_db.default_needed_amount

                    member_item.item_price = item["price"]
                    member_item.item_amount = item["bring_amount"]

                else:
                    member_item = Member_Item_Bringing(user_id=user.id, item_id=item_db.id, item_amount=item["bring_amount"],
                                              session_id=session.id)
                    if "price" in item:
                        member_item.item_price = item["price"]
                    user.item_bringings.append(member_item)
                    item_db.amount_brought += item["bring_amount"]

                if item_db.amount_brought > item_db.amount_needed:
                    item_db.amount_needed = item_db.amount_brought

            for item in item_bring_data["new_items"]:
                item_db = Item(name=item["name"], amount_needed=item["amount"], default_needed_amount=item["amount"], session_id=session.id, amount_brought=item["amount"])
                db.session.add(item_db)
                item = Item.query.filter_by(name=item["name"]).first()
                bringing = Member_Item_Bringing(user_id=user.id, item_id=item.id, session_id=session.id, item_amount=item.amount_needed)
                db.session.add(bringing)

            calculate_session_metrics(session)

            return {"message": "Successfully updated session"}, HTTPStatus.OK

        except ValidationError as e:
            return e.messages, HTTPStatus.BAD_REQUEST


