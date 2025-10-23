"""
Example demonstrating schema validation with Pydantic.

This example shows how to use Pydantic models to validate configuration
and ensure type safety.
"""
import json
import tempfile
import os
from pathlib import Path

# Check if validation support is available
try:
    from pydantic import BaseModel, Field, ValidationError
    from pyconfig_lite import Config, ConfigValidationError
    VALIDATION_AVAILABLE = True
except ImportError:
    print("Pydantic not installed. Install with: pip install pyconfig-lite[validation]")
    VALIDATION_AVAILABLE = False
    exit(1)


# Define configuration schemas using Pydantic models
class DatabaseConfig(BaseModel):
    """Database configuration schema."""
    host: str = Field(..., description="Database hostname")
    port: int = Field(ge=1, le=65535, description="Database port")
    username: str = Field(min_length=1, description="Database username")
    password: str = Field(min_length=8, description="Database password (min 8 chars)")
    database: str = Field(default="myapp", description="Database name")
    max_connections: int = Field(default=10, ge=1, le=100)


class ServerConfig(BaseModel):
    """Server configuration schema."""
    host: str = Field(default="0.0.0.0", description="Server bind address")
    port: int = Field(default=8080, ge=1024, le=65535)
    workers: int = Field(default=4, ge=1, le=32)
    timeout: int = Field(default=30, ge=1)


class LoggingConfig(BaseModel):
    """Logging configuration schema."""
    level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file: str = Field(default="/var/log/myapp.log")


class AppConfig(BaseModel):
    """Full application configuration schema."""
    app_name: str = Field(..., min_length=1, max_length=100)
    debug: bool = Field(default=False)
    secret_key: str = Field(..., min_length=32)
    database: DatabaseConfig
    server: ServerConfig
    logging: LoggingConfig


def main() -> None:
    """Run validation examples."""
    # Create a temporary directory for our example
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"

        # Example 1: Valid configuration
        print("=" * 70)
        print("Example 1: Valid Configuration")
        print("=" * 70)

        valid_config = {
            "app_name": "My Awesome App",
            "debug": True,
            "secret_key": "a" * 32,  # 32 characters minimum
            "database": {
                "host": "localhost",
                "port": 5432,
                "username": "admin",
                "password": "securepass123",
                "database": "production_db",
                "max_connections": 20
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8080,
                "workers": 4,
                "timeout": 60
            },
            "logging": {
                "level": "INFO",
                "format": "%(message)s",
                "file": "/var/log/app.log"
            }
        }

        with open(config_path, 'w') as f:
            json.dump(valid_config, f, indent=2)

        # Load and validate
        config = Config(str(config_path))
        try:
            validated = config.validate(AppConfig)
            print(f"✓ Configuration validated successfully!")
            print(f"  App Name: {validated.app_name}")
            print(f"  Debug Mode: {validated.debug}")
            print(f"  Database: {validated.database.username}@{validated.database.host}:{validated.database.port}")
            print(f"  Server: {validated.server.host}:{validated.server.port} ({validated.server.workers} workers)")
            print(f"  Log Level: {validated.logging.level}")
        except ConfigValidationError as e:
            print(f"✗ Validation failed: {e}")

        # Example 2: Validate specific section
        print("\n" + "=" * 70)
        print("Example 2: Validate Specific Section")
        print("=" * 70)

        try:
            db_config = config.validate_section('database', DatabaseConfig)
            print(f"✓ Database configuration validated!")
            print(f"  Host: {db_config.host}")
            print(f"  Port: {db_config.port}")
            print(f"  Max Connections: {db_config.max_connections}")
        except ConfigValidationError as e:
            print(f"✗ Validation failed: {e}")

        # Example 3: Invalid configuration (port out of range)
        print("\n" + "=" * 70)
        print("Example 3: Invalid Configuration (Port Out of Range)")
        print("=" * 70)

        invalid_config = valid_config.copy()
        invalid_config["server"]["port"] = 70000  # Invalid port

        config_path_invalid = Path(tmpdir) / "invalid_config.json"
        with open(config_path_invalid, 'w') as f:
            json.dump(invalid_config, f, indent=2)

        config_invalid = Config(str(config_path_invalid))
        try:
            validated = config_invalid.validate(AppConfig)
            print(f"✓ Configuration validated (unexpected)")
        except ConfigValidationError as e:
            print(f"✓ Validation correctly failed!")
            print(f"  Error: Port 70000 exceeds valid range (1024-65535)")

        # Example 4: Missing required field
        print("\n" + "=" * 70)
        print("Example 4: Missing Required Field")
        print("=" * 70)

        incomplete_config = {
            "app_name": "Test App",
            # Missing secret_key (required)
            "database": {
                "host": "localhost",
                "port": 5432,
                "username": "admin",
                "password": "password123"
            },
            "server": {},
            "logging": {}
        }

        config_path_incomplete = Path(tmpdir) / "incomplete_config.json"
        with open(config_path_incomplete, 'w') as f:
            json.dump(incomplete_config, f, indent=2)

        config_incomplete = Config(str(config_path_incomplete))
        try:
            validated = config_incomplete.validate(AppConfig)
            print(f"✓ Configuration validated (unexpected)")
        except ConfigValidationError as e:
            print(f"✓ Validation correctly failed!")
            print(f"  Error: Missing required field 'secret_key'")

        # Example 5: Configuration with defaults
        print("\n" + "=" * 70)
        print("Example 5: Using Default Values")
        print("=" * 70)

        minimal_config = {
            "app_name": "Minimal App",
            "secret_key": "x" * 32,
            "database": {
                "host": "db.local",
                "port": 5432,
                "username": "user",
                "password": "password123"
                # database, max_connections will use defaults
            },
            "server": {},  # All will use defaults
            "logging": {}  # All will use defaults
        }

        config_path_minimal = Path(tmpdir) / "minimal_config.json"
        with open(config_path_minimal, 'w') as f:
            json.dump(minimal_config, f, indent=2)

        config_minimal = Config(str(config_path_minimal))
        try:
            validated = config_minimal.validate(AppConfig)
            print(f"✓ Configuration validated with defaults!")
            print(f"  Database Name: {validated.database.database} (default)")
            print(f"  Max Connections: {validated.database.max_connections} (default)")
            print(f"  Server Host: {validated.server.host} (default)")
            print(f"  Server Port: {validated.server.port} (default)")
            print(f"  Workers: {validated.server.workers} (default)")
            print(f"  Log Level: {validated.logging.level} (default)")
        except ConfigValidationError as e:
            print(f"✗ Validation failed: {e}")

        print("\n" + "=" * 70)
        print("✓ All validation examples completed!")
        print("=" * 70)


if __name__ == "__main__":
    main()
