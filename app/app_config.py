import os

class DevelopmentConfig():
    DEBUG = True
    SQLACHEMY_DATABAS_URI = "sqlite:///database.db"
    SECRET_KEY = os.environ.get("SECRET_KEY")
    CORS_HEADERS = "Content-Type"

class ProductionConfig():
    DEBUG = False
    SQLACHEMY_DATABASE_URI = os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://", 1)
    SECRET_KEY = os.environ.get("SECRET_KEY")
    CORS_HEADERS = "Content-Type"
