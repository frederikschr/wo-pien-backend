import os
from app.app_config import DevelopmentConfig, ProductionConfig
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from .models.db import db
from .resources.user import UserResource, ProfileResource, AvatarResource
from .resources.session import SessionResource, SessionEditResource
from .resources.item import ItemBringResource
from .resources.jwt import jwt

def create_app():
    app = Flask(__name__)

    status = os.environ.get("STATUS")
    if status == "Production":
        config = ProductionConfig

    elif status == "Development":
        config = DevelopmentConfig

    app.config.from_object(config)

    db.init_app(app)
    jwt.init_app(app)

    register_resources(app)
    create_database(app)

    CORS(app, resources={r"/*":{'origins':"*"}})

    return app

def register_resources(app):
    api = Api(app)
    api.add_resource(UserResource, "/user")
    api.add_resource(SessionResource, "/session")
    api.add_resource(SessionEditResource, "/session-edit")
    api.add_resource(ItemBringResource, "/bring-items")
    api.add_resource(ProfileResource, "/profile")
    api.add_resource(AvatarResource, "/avatar")

def create_database(app):
    db.create_all(app=app)

