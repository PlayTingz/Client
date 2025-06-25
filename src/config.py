"""
Configuration module for Unity MCP Flask/Quart application.

This module provides environment-based configuration classes and handles
secure secret key generation for different deployment environments.
"""

import os
import secrets
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass(frozen=True)
class UnityMCPSettings:
    """Unity MCP server configuration settings."""
    server_dir: str = os.getenv('UNITY_MCP_SERVER_DIR', '')

    def __post_init__(self):
        if not self.server_dir:
            raise ValueError("UNITY_MCP_SERVER_DIR environment variable is required")


@dataclass(frozen=True)
class ModelSettings:
    """AI model configuration settings."""
    vendor: str = os.getenv('MODEL_VENDOR', 'default')


@dataclass(frozen=True)
class ZeroGSettings:
    """0G (ZeroGravity) service configuration settings."""
    service_api_url: Optional[str] = os.getenv('ZG_SERVICE_API_URL')
    model_name: Optional[str] = os.getenv('ZG_MODEL_NAME')
    model_endpoint: Optional[str] = os.getenv('ZG_MODEL_ENDPOINT')
    provider_address: Optional[str] = os.getenv('ZG_PROVIDER_ADDRESS')


class SecretKeyManager:
    """Manages secure secret key generation and retrieval."""

    @staticmethod
    def get_secret_key(environment: str = 'development') -> str:
        """
        Get SECRET_KEY from environment or generate a secure one.

        Args:
            environment: The current environment (development, production, etc.)

        Returns:
            A secure secret key string

        Raises:
            RuntimeError: If no secret key is provided in production environment
        """
        secret_key = os.getenv('SECRET_KEY')

        if secret_key:
            return secret_key

        if environment == 'production':
            raise RuntimeError(
                "SECRET_KEY environment variable must be set in production. "
                "Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'"
            )

        # Generate temporary key for non-production environments
        generated_key = secrets.token_hex(32)
        print(f"⚠️  Warning: Generated temporary SECRET_KEY for {environment} environment.")
        print("   For production, set SECRET_KEY environment variable.")

        return generated_key

    @staticmethod
    def generate_secret_key() -> str:
        """Generate a new secure secret key."""
        return secrets.token_hex(32)


class BaseConfig:
    """Base configuration class with common settings."""

    # External service settings
    UNITY_MCP = UnityMCPSettings()
    MODEL = ModelSettings()
    ZEROG = ZeroGSettings()

    # Flask/Quart settings
    SECRET_KEY = SecretKeyManager.get_secret_key()

    # Server settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = False  # Default to False, override in specific configs

    # Security settings
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Application settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload

    @classmethod
    def validate_config(cls) -> None:
        """Validate configuration settings."""
        # Add any configuration validation logic here
        pass


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""

    DEVELOPMENT = True
    DEBUG = True
    TESTING = False

    # Development-specific settings
    SESSION_COOKIE_SECURE = False
    HOST = os.getenv('HOST', '127.0.0.1')  # Localhost for development
    PORT = int(os.getenv('PORT', 5000))

    def __init__(self):
        self.SECRET_KEY = SecretKeyManager.get_secret_key('development')


class TestingConfig(BaseConfig):
    """Testing environment configuration."""

    DEVELOPMENT = False
    DEBUG = False
    TESTING = True

    # Testing-specific settings
    SECRET_KEY = SecretKeyManager.generate_secret_key()  # Always generate new key for tests
    WTF_CSRF_ENABLED = False  # Disable CSRF for easier testing
    HOST = os.getenv('HOST', '127.0.0.1')  # Localhost for testing
    PORT = int(os.getenv('PORT', 5001))  # Different port to avoid conflicts


class StagingConfig(BaseConfig):
    """Staging environment configuration."""

    DEVELOPMENT = False
    DEBUG = True  # Keep debug on for staging
    TESTING = False

    # Staging-specific settings
    SESSION_COOKIE_SECURE = True  # Assume HTTPS in staging
    HOST = os.getenv('HOST', '0.0.0.0')  # Accept external connections
    PORT = int(os.getenv('PORT', 8000))  # Different port for staging

    def __init__(self):
        self.SECRET_KEY = SecretKeyManager.get_secret_key('staging')


class ProductionConfig(BaseConfig):
    """Production environment configuration."""

    DEVELOPMENT = False
    DEBUG = False
    TESTING = False

    # Production security settings
    SESSION_COOKIE_SECURE = True  # Require HTTPS
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour session timeout
    HOST = os.getenv('HOST', '0.0.0.0')  # Accept external connections
    PORT = int(os.getenv('PORT', 8080))  # Standard production port

    def __init__(self):
        self.SECRET_KEY = SecretKeyManager.get_secret_key('production')
        self.validate_production_config()

    def validate_production_config(self) -> None:
        """Validate production-specific configuration requirements."""
        required_env_vars = ['SECRET_KEY']
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]

        if missing_vars:
            raise RuntimeError(
                f"Missing required environment variables for production: {', '.join(missing_vars)}"
            )


# Configuration mapping
CONFIG_MAP = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
}


def get_config(config_name: Optional[str] = None) -> BaseConfig:
    """
    Get configuration class based on environment.

    Args:
        config_name: Configuration name (development, testing, staging, production)
                    If None, uses CONFIG_MODE environment variable

    Returns:
        Configuration class instance

    Raises:
        ValueError: If invalid configuration name is provided
    """
    if config_name is None:
        config_name = os.getenv('CONFIG_MODE', 'development')

    if config_name not in CONFIG_MAP:
        raise ValueError(
            f"Invalid configuration: {config_name}. "
            f"Valid options: {', '.join(CONFIG_MAP.keys())}"
        )

    return CONFIG_MAP[config_name]()


# Default system prompt for Unity MCP interactions
DEFAULT_SYSTEM_PROMPT = """
You are a Senior Unity Developer and Technical Lead with deep expertise in Unity Engine, 
C# programming, and game development best practices. You have access to Unity MCP tools 
that allow you to directly interact with the Unity Editor to create, modify, and manage projects.

APPROACH:
1. **Analyze & Plan**: Before taking action, carefully analyze the request and formulate 
   a clear, step-by-step plan
2. **Explain Your Reasoning**: Share your thought process and explain why you're choosing 
   specific approaches
3. **Execute Methodically**: Use tools systematically, explaining each step as you go
4. **Adapt & Problem-Solve**: If issues arise, diagnose problems, explain what went wrong, 
   and adjust your approach

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

When working with tools, always verify results and handle errors gracefully. Your goal is 
not just to complete tasks, but to help users understand Unity development concepts and 
improve their skills.
""".strip()

# Backward compatibility
config = CONFIG_MAP  # For existing code that uses config['development']