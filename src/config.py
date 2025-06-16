import os
import secrets
from dotenv import load_dotenv
load_dotenv()

# MCP API credentials
MCP_API_KEY = os.getenv('MCP_API_KEY')
UNITY_MCP_SERVER_DIR = os.getenv('UNITY_MCP_SERVER_DIR')

def get_secret_key():
    """Get SECRET_KEY from environment or generate a secure one."""
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        # Generate a secure random key for this session
        # In production, you should set SECRET_KEY explicitly
        secret_key = secrets.token_hex(32)  # 64 character hex string
        if os.getenv('FLASK_ENV') != 'production':
            print(f"Warning: Generated temporary SECRET_KEY. For production, set SECRET_KEY environment variable.")
    return secret_key

class Config:
    SECRET_KEY = get_secret_key()
    DEVELOPMENT = True
    TESTING = True
    DEBUG = True

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    # Generate a different key for testing
    SECRET_KEY = secrets.token_hex(32)

class StagingConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("STAGING_DATABASE_URL")
    MONGODB_SETTINGS = {
        'db': 'jarvis-staging',
        'host': os.getenv("MONGODB_URI")
    }

class ProductionConfig(Config):
    DEVELOPMENT = False
    TESTING = False
    DEBUG = False
    # Production should always have explicit SECRET_KEY
    SECRET_KEY = os.getenv('SECRET_KEY') or secrets.token_hex(32)

config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
}
