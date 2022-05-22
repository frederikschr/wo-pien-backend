import os

class Config():
    SECRET_KEY = os.urandom(24)
    CORS_HEADERS = "Content-Type"

class DevelopmentConfig(Config):
    DEBUG = True
    SQLACHEMY_DATABAS_URI = "sqlite:///database.db"

class ProductionConfig(Config):
    DEBUG = False
    SQLACHEMY_DATABASE_URI = os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://", 1)