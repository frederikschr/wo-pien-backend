from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from http import HTTPStatus
from marshmallow import ValidationError
from ..models.db import db
from ..models.item import Item
from ..models.user import User, MemberItems
from ..models.session import Session
from ..schemas.item.item_bring import ItemBringSchema
from ..utils import member_items_to_dict

class ItemBringResource(Resource):
    @jwt_required()
    def patch(self):
        json_data = request.get_json()
        user = User.query.get(get_jwt_identity())
        json_data["user_id"] = get_jwt_identity()
        item_bring_schema = ItemBringSchema()
        try:
            item_bring_data = item_bring_schema.load(data=json_data)

            session = Session.query.get(item_bring_data["session_id"])

            for item in item_bring_data["removed_items"]:
                item_db = Item.query.get(item["id"])
                member_item = MemberItems.query.get((user.id, item_db.id))
                db.session.delete(member_item)
                item_db.amount_brought -= item["bring_amount"]

            for item in item_bring_data["updated_items"]:

                item_db = Item.query.get(item["id"])
                member_item = MemberItems.query.get((user.id, item_db.id))

                if member_item:

                    item_db.amount_brought += (int(item["bring_amount"]) - member_item.item_amount)

                    if item_db.amount_brought < item_db.amount and item_db.amount > item_db.start_amount:
                        if item["bring_amount"] >= item_db.start_amount:
                            item_db.amount -= (member_item.item_amount - item["bring_amount"])
                        else:
                            item_db.amount = item_db.start_amount

                    member_item.item_price = item["price"]
                    member_item.item_amount = item["bring_amount"]

                else:
                    member_item = MemberItems(user_id=user.id, item_id=item_db.id, item_amount=item["bring_amount"],
                                              session_id=session.id)
                    if "price" in item:
                        member_item.item_price = item["price"]
                    user.items.append(member_item)
                    item_db.amount_brought += item["bring_amount"]

                if item_db.amount_brought > item_db.amount:
                    item_db.amount = item_db.amount_brought


            for item in item_bring_data["new_items"]:
                item_db = Item(name=item["name"], amount=item["amount"], start_amount=item["amount"], session_id=session.id, amount_brought=item["amount"])
                db.session.add(item_db)
                item = Item.query.filter_by(name=item["name"]).first()
                bringing = MemberItems(user_id=user.id, item_id=item.id, session_id=session.id, item_amount=item.amount)
                db.session.add(bringing)

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
            session.bringings = member_items_to_dict(session)

            db.session.commit()

            return {"message": "Successfully updated session"}, HTTPStatus.OK

        except ValidationError as e:
            return e.messages, HTTPStatus.BAD_REQUEST


