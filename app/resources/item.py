from flask_restful import Resource
from flask import request
from marshmallow import ValidationError
from http import HTTPStatus
from app.resources.jwt import *
from app.models.db import db
from app.models.item import Item

class ItemResource(Resource):
    @jwt_required()
    def patch(self):
        json_data = request.get_json()
        for item in json_data["updated_items"]:
            item_db = Item.query.get(item["id"])
            if item_db:
                item_db.name = item["name"]
                item_db.amount = item["amount"]
                item_db.price = item["price"]
                item_db.amount_brought = item["amount_brought"]
            db.session.commit()
        return HTTPStatus.OK


