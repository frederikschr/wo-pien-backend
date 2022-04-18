from flask_restful import Resource
from flask import request
from http import HTTPStatus
from app.resources.jwt import *
from app.models.db import db
from app.models.item import Item
from app.models.user import User, MemberItems

class ItemBringResource(Resource):
    @jwt_required()
    def patch(self):
        json_data = request.get_json()
        user = User.query.get(get_jwt_identity())
        for item in json_data["updated_items"]:
            item_db = Item.query.get(item["id"])
            if item_db and user in item_db.session.members:
                if item_db.byHost and user.id != item_db.session.owner_id:
                    return HTTPStatus.UNAUTHORIZED

                elif not item_db.byHost and user.id == item_db.session.owner_id:
                    item_db.byHost = True

                if member_item := MemberItems.query.get((user.id, item_db.id)):
                    member_item.item_price = item["price"]
                    member_item.item_amount = item["bring_amount"]
                    if member_item.item_amount != item["bring_amount"]:
                        if item_db.amount_brought > item["bring_amount"]:
                            item_db.amount_brought += item["bring_amount"]
                        else:
                            item_db.amount_brought -= item_db.amount_brought - item["bring_amount"]
                else:
                    member_item = MemberItems(user_id=user.id, item_id=item_db.id, item_amount=item["bring_amount"], item_price=item["price"])
                    user.items.append(member_item)
                    item_db.amount_brought += item["bring_amount"]

            else:
                print("item does not exist")

        db.session.commit()

        return HTTPStatus.OK


class ItemManageResource(Resource):
    pass
