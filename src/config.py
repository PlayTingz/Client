# config.py
import os
from dotenv import load_dotenv
load_dotenv()

# MCP API credentials
MCP_API_KEY = os.getenv('MCP_API_KEY')

class Config:
    DEVELOPMENT = True
    TESTING = True
    DEBUG = True
class DevelopmentConfig(Config):
    DEBUG = True
class TestingConfig(Config):
    TESTING = True
class StagingConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("STAGING_DATABASE_URL")
    MONGODB_SETTINGS =  {
        'db': 'jarvis-staging',
        'host': os.getenv("MONGODB_URI")
    }
class ProductionConfig(Config):
    DEVELOPMENT = False
    TESTING = False
    DEBUG = False
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
}