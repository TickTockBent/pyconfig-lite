"""
Example demonstrating .env file support.

Shows how to use .env files for local development and environment variable management.
"""
import json
import tempfile
from pathlib import Path
from liteconfig_py import Config


def main() -> None:
    """Run .env file examples."""
    print("=" * 70)
    print(".env File Support Example")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create a base configuration file
        config_data = {
            "app": {
                "name": "My Application",
                "port": 8080,
                "debug": False
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "myapp",
                "user": "default_user"
            },
            "api": {
                "key": "default_api_key",
                "endpoint": "https://api.example.com"
            }
        }

        config_path = tmpdir / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)

        # Example 1: Load config without .env
        print("\n" + "=" * 70)
        print("Example 1: Configuration Without .env File")
        print("=" * 70)

        config_no_env = Config(str(config_path))
        print(f"App Port:      {config_no_env.get('app.port')}")
        print(f"Database Host: {config_no_env.get('database.host')}")
        print(f"Database User: {config_no_env.get('database.user')}")
        print(f"API Key:       {config_no_env.get('api.key')}")

        # Example 2: Create and load .env file
        print("\n" + "=" * 70)
        print("Example 2: Configuration With .env File")
        print("=" * 70)

        env_path = tmpdir / ".env"
        with open(env_path, 'w') as f:
            f.write("""# Application .env file
# Override configuration values for local development

# Application settings
APP_PORT=3000
APP_DEBUG=true

# Database configuration
DATABASE_HOST=db.local.dev
DATABASE_USER=dev_user
DATABASE_PASSWORD=dev_password_123

# API configuration
API_KEY=dev_api_key_xyz789
API_ENDPOINT=https://api.dev.example.com
""")

        print(f"Created .env file at: {env_path}\n")
        print("Contents:")
        print("-" * 70)
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    print(f"  {line.rstrip()}")
        print("-" * 70)

        config_with_env = Config(
            str(config_path),
            load_dotenv=True,
            dotenv_path=str(env_path)
        )

        print(f"\nConfiguration values after loading .env:")
        print(f"App Port:      {config_with_env.get('app.port')} (overridden)")
        print(f"App Debug:     {config_with_env.get('app.debug')} (overridden)")
        print(f"Database Host: {config_with_env.get('database.host')} (overridden)")
        print(f"Database User: {config_with_env.get('database.user')} (overridden)")
        print(f"Database Pass: {config_with_env.get('database.password')} (from .env)")
        print(f"API Key:       {config_with_env.get('api.key')} (overridden)")

        # Example 3: .env with various value formats
        print("\n" + "=" * 70)
        print("Example 3: .env With Different Value Formats")
        print("=" * 70)

        env_formats = tmpdir / ".env.formats"
        with open(env_formats, 'w') as f:
            f.write("""# Different value formats in .env

# Plain values
PLAIN_VALUE=simple_text

# Quoted values
SINGLE_QUOTED='value with spaces'
DOUBLE_QUOTED="another value with spaces"

# Numbers (parsed as strings then converted)
NUMBER_VALUE=42
FLOAT_VALUE=3.14

# Boolean values
BOOL_TRUE=true
BOOL_FALSE=false

# JSON arrays
JSON_ARRAY=["item1", "item2", "item3"]

# JSON objects
JSON_OBJECT={"key": "value", "nested": {"data": true}}

# URLs and special characters
DATABASE_URL=postgresql://user:pass@localhost:5432/db
API_ENDPOINT=https://api.example.com/v1?key=abc123&format=json
""")

        config_formats = Config(
            str(config_path),
            load_dotenv=True,
            dotenv_path=str(env_formats)
        )

        print("Value type demonstrations:")
        print(f"Plain:       {config_formats.get('plain.value')} (str)")
        print(f"Single:      {config_formats.get('single.quoted')} (str)")
        print(f"Double:      {config_formats.get('double.quoted')} (str)")
        print(f"Number:      {config_formats.get('number.value')} (parsed to int)")
        print(f"Float:       {config_formats.get('float.value')} (parsed to float)")
        print(f"Bool True:   {config_formats.get('bool.true')} (parsed to bool)")
        print(f"Bool False:  {config_formats.get('bool.false')} (parsed to bool)")
        print(f"JSON Array:  {config_formats.get('json.array')}")
        print(f"JSON Object: {config_formats.get('json.object')}")

        # Example 4: Environment-specific .env files
        print("\n" + "=" * 70)
        print("Example 4: Environment-Specific .env Files")
        print("=" * 70)

        # .env.local
        env_local = tmpdir / ".env.local"
        with open(env_local, 'w') as f:
            f.write("""DATABASE_HOST=localhost
DEBUG=true
""")

        # .env.test
        env_test = tmpdir / ".env.test"
        with open(env_test, 'w') as f:
            f.write("""DATABASE_HOST=test-db
DEBUG=true
""")

        # .env.production
        env_prod = tmpdir / ".env.production"
        with open(env_prod, 'w') as f:
            f.write("""DATABASE_HOST=prod-db.example.com
DEBUG=false
""")

        for env_name, env_file in [("local", env_local), ("test", env_test), ("production", env_prod)]:
            cfg = Config(str(config_path), load_dotenv=True, dotenv_path=str(env_file))
            print(f"{env_name:12} -> DB: {cfg.get('database.host'):25} Debug: {cfg.get('debug', False)}")

        # Best practices
        print("\n" + "=" * 70)
        print("Best Practices for .env Files")
        print("=" * 70)
        print("1. ✓ Use .env for local development configuration")
        print("2. ✓ Add .env to .gitignore (never commit secrets!)")
        print("3. ✓ Provide .env.example as a template")
        print("4. ✓ Use environment-specific files (.env.development, .env.test, etc.)")
        print("5. ✓ Document required environment variables")
        print("6. ✗ Don't put production secrets in .env files")
        print("7. ✓ Use secret management systems for production (Vault, AWS Secrets, etc.)")
        print("=" * 70)

        # Example .env.example file
        print("\n" + "=" * 70)
        print("Example: .env.example Template")
        print("=" * 70)

        env_example = tmpdir / ".env.example"
        with open(env_example, 'w') as f:
            f.write("""# Application Configuration Template
# Copy this file to .env and fill in your values

# Application Settings
APP_PORT=8080
APP_DEBUG=false

# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=myapp
DATABASE_USER=your_username
DATABASE_PASSWORD=your_password

# API Keys (get from https://example.com/api)
API_KEY=your_api_key_here
API_ENDPOINT=https://api.example.com

# Optional: External Services
# REDIS_URL=redis://localhost:6379
# SENTRY_DSN=your_sentry_dsn
""")

        print("\nCreate a .env.example file for your team:")
        print("-" * 70)
        with open(env_example, 'r') as f:
            print(f.read())
        print("-" * 70)


if __name__ == "__main__":
    main()
