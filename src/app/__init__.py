import os
import socket
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_migrate import Migrate
from .models.user import User
from .models.db import db
from .models.statistics import Statistics
from .resources.user import UserResource, ProfileResource, AvatarResource
from .resources.session import SessionResource, SessionEditResource
from .resources.item import ItemBringResource
from .resources.jwt import jwt

def create_app():
    app = Flask(__name__)

    status = os.environ.get("STATUS")

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["CORS_HEADERS"] = "Content-Type"

    migrate = Migrate()
    
    if status == "Production":
        print("Loading Production config...")
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://", 1)
        app.config["DEBUG"] = False

    elif status == "Development":
        print("Loading Development config...")
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
        app.config["DEBUG"] = True

    db.init_app(app)
    jwt.init_app(app)

    migrate.init_app(app, db)

    register_resources(app)
    create_database(app)

    CORS(app, resources={r"/*":{'origins':"*"}})

    @app.route('/')
    def home():
        return f"Welcome to WoPien backend from Host / Container: {socket.gethostname()}!"

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
