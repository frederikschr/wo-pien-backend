import os

from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from .models.db import db
from .resources.user import UserResource
from .resources.session import SessionResource, SessionEditResource
from .resources.item import ItemResource
from .resources.jwt import jwt

app = Flask(__name__)

def create_app():
    #app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["SECRET_KEY"] = "secret!"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
    app.config['CORS_HEADERS'] = 'Content-Type'

    db.init_app(app)
    jwt.init_app(app)

    register_resources()

    create_database(app)

    CORS(app, resources={r"/*":{'origins':"*"}})

    return app

def register_resources():
    api = Api(app)
    api.add_resource(UserResource, "/user")
    api.add_resource(SessionResource, "/session")
    api.add_resource(SessionEditResource, "/session-edit")
    api.add_resource(ItemResource, "/bring-items")

def create_database(app):
    db.create_all(app=app)
    print("Created database")
