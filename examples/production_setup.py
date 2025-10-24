"""
Production-ready configuration setup example.

Demonstrates best practices for production deployments including:
- Configuration validation
- Secret management
- Error handling
- Logging configuration
- Health checks
"""
import json
import logging
import sys
import tempfile
from pathlib import Path
from typing import Optional

try:
    from pydantic import BaseModel, Field, SecretStr, validator
    VALIDATION_AVAILABLE = True
except ImportError:
    print("Warning: Pydantic not available. Install with: pip install liteconfig_py[validation]")
    VALIDATION_AVAILABLE = False

from liteconfig_py import Config


# Define strict production configuration schema
if VALIDATION_AVAILABLE:
    class DatabaseConfig(BaseModel):
        """Production database configuration."""
        host: str = Field(..., min_length=1)
        port: int = Field(..., ge=1, le=65535)
        name: str = Field(..., min_length=1)
        username: str = Field(..., min_length=1)
        password: SecretStr = Field(..., min_length=8)
        ssl_mode: str = Field(default="require", pattern="^(disable|allow|prefer|require|verify-ca|verify-full)$")
        pool_size: int = Field(default=20, ge=5, le=100)
        pool_timeout: int = Field(default=30, ge=1)

        @validator('host')
        def validate_host(cls, v: str) -> str:
            """Ensure host is not localhost in production."""
            if v.lower() in ['localhost', '127.0.0.1', '0.0.0.0']:
                raise ValueError("Production database must not use localhost")
            return v


    class RedisConfig(BaseModel):
        """Redis cache configuration."""
        host: str
        port: int = Field(default=6379, ge=1, le=65535)
        password: Optional[SecretStr] = None
        db: int = Field(default=0, ge=0, le=15)
        ssl: bool = Field(default=True)
        socket_timeout: int = Field(default=5, ge=1)


    class SecurityConfig(BaseModel):
        """Security settings."""
        secret_key: SecretStr = Field(..., min_length=32)
        allowed_hosts: list[str] = Field(..., min_items=1)
        cors_origins: list[str] = Field(default_factory=list)
        rate_limit: int = Field(default=100, ge=1)
        session_timeout: int = Field(default=3600, ge=300)

        @validator('secret_key')
        def validate_secret_key(cls, v: SecretStr) -> SecretStr:
            """Ensure secret key is strong."""
            key = v.get_secret_value()
            if key == "changeme" or key.count('a') > len(key) // 2:
                raise ValueError("Secret key appears to be weak or default")
            return v


    class LoggingConfig(BaseModel):
        """Logging configuration."""
        level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
        format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file: Optional[str] = None
        max_bytes: int = Field(default=10485760, ge=1024)  # 10MB
        backup_count: int = Field(default=5, ge=1, le=50)


    class MonitoringConfig(BaseModel):
        """Monitoring and observability."""
        enabled: bool = Field(default=True)
        metrics_port: int = Field(default=9090, ge=1024, le=65535)
        health_check_interval: int = Field(default=30, ge=5)
        sentry_dsn: Optional[str] = None


    class ProductionConfig(BaseModel):
        """Complete production configuration."""
        environment: str = Field(..., pattern="^(production|prod)$")
        debug: bool = Field(default=False)
        database: DatabaseConfig
        redis: RedisConfig
        security: SecurityConfig
        logging: LoggingConfig
        monitoring: MonitoringConfig

        @validator('debug')
        def validate_debug_in_production(cls, v: bool, values: dict) -> bool:
            """Ensure debug is False in production."""
            if v and values.get('environment', '').startswith('prod'):
                raise ValueError("Debug mode must be disabled in production")
            return v


def setup_logging(config: Config) -> None:
    """Configure application logging."""
    log_level = config.get('logging.level', 'INFO')
    log_format = config.get('logging.format')

    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )


def validate_production_config(config: Config) -> Optional['ProductionConfig']:
    """Validate production configuration with detailed error reporting."""
    if not VALIDATION_AVAILABLE:
        logging.warning("Pydantic not available - skipping validation")
        return None

    try:
        validated = config.validate(ProductionConfig)
        logging.info("✓ Configuration validation passed")
        return validated
    except Exception as e:
        logging.error(f"✗ Configuration validation failed: {e}")
        logging.error("Please fix configuration errors before starting the application")
        sys.exit(1)


def check_configuration_health(config: Config) -> bool:
    """Perform basic configuration health checks."""
    checks_passed = True

    # Check database configuration
    if not config.get('database.host'):
        logging.error("Database host not configured")
        checks_passed = False

    # Check security settings
    secret_key = config.get('security.secret_key', '')
    if len(secret_key) < 32:
        logging.error("Secret key is too short (minimum 32 characters)")
        checks_passed = False

    # Check allowed hosts
    allowed_hosts = config.get('security.allowed_hosts', [])
    if not allowed_hosts or '*' in allowed_hosts:
        logging.warning("Allowed hosts is not properly configured")

    # Check debug mode
    if config.get('debug', False):
        logging.warning("Debug mode is enabled - should be disabled in production!")
        checks_passed = False

    return checks_passed


def create_example_production_config(tmpdir: Path) -> tuple[str, str]:
    """Create example production configuration files."""
    # Main configuration file
    config_data = {
        "environment": "production",
        "debug": False,
        "database": {
            "host": "db-cluster.prod.internal",
            "port": 5432,
            "name": "myapp_production",
            "username": "app_user",
            "password": "placeholder",  # Will be overridden by .env
            "ssl_mode": "require",
            "pool_size": 20,
            "pool_timeout": 30
        },
        "redis": {
            "host": "redis.prod.internal",
            "port": 6379,
            "password": "placeholder",  # Will be overridden by .env
            "db": 0,
            "ssl": True,
            "socket_timeout": 5
        },
        "security": {
            "secret_key": "placeholder",  # Will be overridden by .env
            "allowed_hosts": ["app.example.com", "www.example.com"],
            "cors_origins": ["https://app.example.com"],
            "rate_limit": 100,
            "session_timeout": 3600
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "/var/log/myapp/app.log",
            "max_bytes": 10485760,
            "backup_count": 5
        },
        "monitoring": {
            "enabled": True,
            "metrics_port": 9090,
            "health_check_interval": 30,
            "sentry_dsn": None
        }
    }

    config_path = tmpdir / "config.production.json"
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=2)

    # Create .env file with secrets
    env_path = tmpdir / ".env.production"
    with open(env_path, 'w') as f:
        f.write("""# Production Environment Variables
# WARNING: Never commit this file to version control!

# Database credentials
DATABASE_PASSWORD=super_secure_db_password_123!

# Redis credentials
REDIS_PASSWORD=super_secure_redis_password_456!

# Application secrets
SECURITY_SECRET_KEY=abcdef1234567890abcdef1234567890abcdef1234567890

# Monitoring (optional)
# MONITORING_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
""")

    return str(config_path), str(env_path)


def main() -> None:
    """Demonstrate production configuration setup."""
    print("=" * 70)
    print("Production Configuration Setup Example")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create example config files
        config_path, env_path = create_example_production_config(tmpdir)

        print(f"\nCreated configuration files:")
        print(f"  Config: {config_path}")
        print(f"  Secrets: {env_path}")

        # Load configuration
        print("\n" + "=" * 70)
        print("Loading Production Configuration")
        print("=" * 70)

        try:
            config = Config(
                config_path,
                load_dotenv=True,
                dotenv_path=env_path
            )
            print("✓ Configuration loaded successfully")
        except Exception as e:
            print(f"✗ Failed to load configuration: {e}")
            sys.exit(1)

        # Setup logging
        setup_logging(config)
        logger = logging.getLogger(__name__)

        # Perform health checks
        print("\n" + "=" * 70)
        print("Configuration Health Checks")
        print("=" * 70)

        if check_configuration_health(config):
            logger.info("✓ All health checks passed")
        else:
            logger.error("✗ Some health checks failed")

        # Validate configuration
        print("\n" + "=" * 70)
        print("Configuration Validation")
        print("=" * 70)

        validated_config = validate_production_config(config)

        if validated_config:
            print("\n" + "=" * 70)
            print("Configuration Summary")
            print("=" * 70)
            print(f"Environment:        {validated_config.environment}")
            print(f"Debug Mode:         {validated_config.debug}")
            print(f"Database Host:      {validated_config.database.host}")
            print(f"Database Name:      {validated_config.database.name}")
            print(f"Database Pool Size: {validated_config.database.pool_size}")
            print(f"Redis Host:         {validated_config.redis.host}")
            print(f"Redis SSL:          {validated_config.redis.ssl}")
            print(f"Allowed Hosts:      {', '.join(validated_config.security.allowed_hosts)}")
            print(f"Log Level:          {validated_config.logging.level}")
            print(f"Monitoring:         {'Enabled' if validated_config.monitoring.enabled else 'Disabled'}")

        print("\n" + "=" * 70)
        print("Production Deployment Checklist")
        print("=" * 70)
        print("✓ Configuration files created")
        print("✓ Secrets loaded from .env file")
        print("✓ Configuration validated")
        print("✓ Health checks passed")
        print("✓ Logging configured")
        print("\n⚠ Remember to:")
        print("  - Never commit .env files to version control")
        print("  - Use strong, unique passwords for all services")
        print("  - Enable SSL/TLS for all connections")
        print("  - Set up proper monitoring and alerting")
        print("  - Regularly rotate secrets and credentials")
        print("  - Review and update allowed_hosts list")
        print("  - Configure proper backup strategies")
        print("=" * 70)


if __name__ == "__main__":
    main()
