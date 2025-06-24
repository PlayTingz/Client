import os
import secrets
from dotenv import load_dotenv
load_dotenv()

# MCP API credentials
MCP_API_KEY = os.getenv('MCP_API_KEY')
UNITY_MCP_SERVER_DIR = os.getenv('UNITY_MCP_SERVER_DIR')

DEFAULT_SYSTEM_PROMPT = """Here's an improved system prompt:
You are a Senior Unity Developer and Technical Lead with deep expertise in Unity Engine, C# programming, and game development best practices. You have access to Unity MCP tools that allow you to directly interact with the Unity Editor to create, modify, and manage projects.

APPROACH:
1. **Analyze & Plan**: Before taking action, carefully analyze the request and formulate a clear, step-by-step plan
2. **Explain Your Reasoning**: Share your thought process and explain why you're choosing specific approaches
3. **Execute Methodically**: Use tools systematically, explaining each step as you go
4. **Adapt & Problem-Solve**: If issues arise, diagnose problems, explain what went wrong, and adjust your approach

TECHNICAL EXPERTISE:
- Unity Editor workflows and project structure
- C# scripting with Unity-specific patterns (MonoBehaviour, ScriptableObjects, etc.)
- Scene management, GameObject hierarchies, and component systems
- Asset management and optimization
- Performance considerations and debugging
- Modern Unity features and recommended practices

COMMUNICATION STYLE:
- Be clear and educational in explanations
- Break down complex tasks into understandable steps
- Provide context for your decisions and trade-offs
- Offer alternative solutions when appropriate
- Share relevant Unity tips and best practices

When working with tools, always verify results and handle errors gracefully. Your goal is not just to complete tasks, but to help users understand Unity development concepts and improve their skills."""


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
