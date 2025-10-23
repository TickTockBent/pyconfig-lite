"""
Example demonstrating multi-environment configuration management.

Shows how to manage configurations for different environments
(development, staging, production) using environment variables and .env files.
"""
import json
import tempfile
import os
from pathlib import Path
from pyconfig_lite import Config


def create_environment_configs(tmpdir: Path) -> dict:
    """Create configuration files for different environments."""
    configs = {}

    # Base configuration (shared across all environments)
    base_config = {
        "app": {
            "name": "MyApp",
            "version": "1.0.0"
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "myapp",
            "pool_size": 5
        },
        "cache": {
            "enabled": True,
            "ttl": 300
        },
        "features": {
            "analytics": True,
            "notifications": True
        }
    }

    # Development environment overrides
    dev_config = base_config.copy()
    dev_config.update({
        "debug": True,
        "log_level": "DEBUG",
        "database": {
            **base_config["database"],
            "host": "localhost",
            "name": "myapp_dev"
        }
    })

    # Staging environment overrides
    staging_config = base_config.copy()
    staging_config.update({
        "debug": False,
        "log_level": "INFO",
        "database": {
            **base_config["database"],
            "host": "staging-db.example.com",
            "name": "myapp_staging",
            "pool_size": 10
        }
    })

    # Production environment overrides
    prod_config = base_config.copy()
    prod_config.update({
        "debug": False,
        "log_level": "WARNING",
        "database": {
            **base_config["database"],
            "host": "prod-db.example.com",
            "name": "myapp_production",
            "pool_size": 20
        },
        "cache": {
            "enabled": True,
            "ttl": 600
        }
    })

    # Write config files
    for env, config_data in [
        ("dev", dev_config),
        ("staging", staging_config),
        ("prod", prod_config)
    ]:
        config_path = tmpdir / f"config.{env}.json"
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        configs[env] = str(config_path)

    return configs


def create_env_files(tmpdir: Path) -> dict:
    """.env files for each environment."""
    env_files = {}

    # Development .env
    dev_env = tmpdir / ".env.development"
    with open(dev_env, 'w') as f:
        f.write("""# Development Environment
APP_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=myapp_dev
SECRET_KEY=dev-secret-key-not-for-production
""")
    env_files["dev"] = str(dev_env)

    # Staging .env
    staging_env = tmpdir / ".env.staging"
    with open(staging_env, 'w') as f:
        f.write("""# Staging Environment
APP_ENV=staging
DEBUG=false
LOG_LEVEL=INFO
DATABASE_HOST=staging-db.internal
DATABASE_PORT=5432
DATABASE_NAME=myapp_staging
DATABASE_POOL_SIZE=15
SECRET_KEY=staging-secret-key-change-me
""")
    env_files["staging"] = str(staging_env)

    # Production .env
    prod_env = tmpdir / ".env.production"
    with open(prod_env, 'w') as f:
        f.write("""# Production Environment
APP_ENV=production
DEBUG=false
LOG_LEVEL=WARNING
DATABASE_HOST=prod-db-cluster.internal
DATABASE_PORT=5432
DATABASE_NAME=myapp_production
DATABASE_POOL_SIZE=50
CACHE_TTL=3600
SECRET_KEY=super-secret-production-key
""")
    env_files["prod"] = str(prod_env)

    return env_files


def display_config(config: Config, environment: str) -> None:
    """Display configuration values."""
    print(f"\n{'=' * 70}")
    print(f"Environment: {environment.upper()}")
    print(f"{'=' * 70}")
    print(f"App Name:           {config.get('app.name')}")
    print(f"App Version:        {config.get('app.version')}")
    print(f"Debug Mode:         {config.get('debug')}")
    print(f"Log Level:          {config.get('log.level', config.get('log_level'))}")
    print(f"Database Host:      {config.get('database.host')}")
    print(f"Database Name:      {config.get('database.name')}")
    print(f"Database Pool Size: {config.get('database.pool.size', config.get('database.pool_size'))}")
    print(f"Cache Enabled:      {config.get('cache.enabled')}")
    print(f"Cache TTL:          {config.get('cache.ttl')}")
    print(f"Secret Key:         {config.get('secret.key', 'not set')[:20]}...")


def main() -> None:
    """Run multi-environment configuration examples."""
    print("=" * 70)
    print("Multi-Environment Configuration Management Example")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create configuration files
        config_files = create_environment_configs(tmpdir)
        env_files = create_env_files(tmpdir)

        # Example 1: Load development configuration
        print("\n" + "=" * 70)
        print("Example 1: Development Environment (Config File Only)")
        print("=" * 70)
        dev_config = Config(config_files["dev"])
        display_config(dev_config, "development")

        # Example 2: Load development with .env file
        print("\n" + "=" * 70)
        print("Example 2: Development Environment (With .env File)")
        print("=" * 70)
        dev_config_with_env = Config(
            config_files["dev"],
            load_dotenv=True,
            dotenv_path=env_files["dev"]
        )
        display_config(dev_config_with_env, "development (with .env)")

        # Example 3: Staging environment
        print("\n" + "=" * 70)
        print("Example 3: Staging Environment")
        print("=" * 70)
        staging_config = Config(
            config_files["staging"],
            load_dotenv=True,
            dotenv_path=env_files["staging"]
        )
        display_config(staging_config, "staging")

        # Example 4: Production environment
        print("\n" + "=" * 70)
        print("Example 4: Production Environment")
        print("=" * 70)
        prod_config = Config(
            config_files["prod"],
            load_dotenv=True,
            dotenv_path=env_files["prod"]
        )
        display_config(prod_config, "production")

        # Example 5: Environment-specific prefix
        print("\n" + "=" * 70)
        print("Example 5: Using Environment Variable Prefix")
        print("=" * 70)
        print("This allows multiple apps to coexist with different configs")

        # Set some environment variables with prefix
        os.environ['MYAPP_DATABASE_HOST'] = 'custom-db.example.com'
        os.environ['MYAPP_DATABASE_PORT'] = '3306'
        os.environ['MYAPP_CACHE_TTL'] = '1800'

        prefixed_config = Config(
            config_files["dev"],
            env_prefix='MYAPP_'
        )

        print(f"\nWith MYAPP_ prefix:")
        print(f"  Database Host: {prefixed_config.get('database.host')}")
        print(f"  Database Port: {prefixed_config.get('database.port')}")
        print(f"  Cache TTL: {prefixed_config.get('cache.ttl')}")

        # Example 6: Selecting environment at runtime
        print("\n" + "=" * 70)
        print("Example 6: Dynamic Environment Selection")
        print("=" * 70)

        def load_config_for_environment(env: str) -> Config:
            """Load configuration based on environment."""
            if env not in config_files or env not in env_files:
                raise ValueError(f"Unknown environment: {env}")

            return Config(
                config_files[env],
                load_dotenv=True,
                dotenv_path=env_files[env]
            )

        # Simulate environment selection
        for env in ["dev", "staging", "prod"]:
            config = load_config_for_environment(env)
            print(f"\n{env.upper()}: DB={config.get('database.host')}, "
                  f"Debug={config.get('debug')}, "
                  f"Pool={config.get('database.pool.size', config.get('database.pool_size'))}")

        print("\n" + "=" * 70)
        print("Best Practices:")
        print("=" * 70)
        print("1. Use base config + environment-specific overrides")
        print("2. Never commit .env files with secrets to version control")
        print("3. Use .env.example as a template for required variables")
        print("4. Use env_prefix to avoid conflicts in shared environments")
        print("5. Validate configs on startup to catch issues early")
        print("6. Keep development configs permissive, production restrictive")
        print("=" * 70)


if __name__ == "__main__":
    main()
