# liteconfig_py Examples

This directory contains comprehensive examples demonstrating various features and use cases of liteconfig_py.

## Running the Examples

All examples are self-contained and can be run directly:

```bash
python examples/basic_usage.py
python examples/validation_example.py
python examples/multi_env_example.py
python examples/production_setup.py
python examples/dotenv_example.py
```

## Available Examples

### 1. basic_usage.py
**Basic Configuration Loading**

Demonstrates the fundamental features of liteconfig_py:
- Loading configuration from YAML and JSON files
- Accessing nested configuration values with dot notation
- Using default values for missing keys
- Environment variable overrides
- Dictionary-style access

**Run it:**
```bash
python examples/basic_usage.py
```

### 2. validation_example.py
**Schema Validation with Pydantic**

Shows how to use Pydantic models for type-safe configuration validation:
- Defining configuration schemas with Pydantic
- Validating entire configurations
- Validating specific configuration sections
- Using field constraints (min/max values, patterns, etc.)
- Handling validation errors
- Working with default values

**Prerequisites:**
```bash
pip install liteconfig_py[validation]
```

**Run it:**
```bash
python examples/validation_example.py
```

**Key Features Demonstrated:**
- Type safety and automatic type coercion
- Field validation with constraints
- Nested model validation
- Custom validators
- Error handling

### 3. multi_env_example.py
**Multi-Environment Configuration Management**

Demonstrates managing configurations across different environments:
- Separate config files for dev/staging/production
- Environment-specific .env files
- Configuration inheritance and overrides
- Using environment variable prefixes
- Dynamic environment selection at runtime

**Run it:**
```bash
python examples/multi_env_example.py
```

**Best Practices:**
- Base configuration + environment-specific overrides
- Never commit .env files with secrets
- Use .env.example as a template
- Validate configs on startup

### 4. production_setup.py
**Production-Ready Configuration Setup**

A comprehensive example for production deployments:
- Strict configuration validation
- Secret management with .env files
- Security best practices
- Logging configuration
- Health checks and monitoring setup
- Configuration validation with detailed error reporting

**Prerequisites:**
```bash
pip install liteconfig_py[validation]
```

**Run it:**
```bash
python examples/production_setup.py
```

**Features:**
- Production-ready security settings
- Database connection pooling
- Redis cache configuration
- Monitoring and metrics setup
- Deployment checklist

### 5. dotenv_example.py
**.env File Support**

Comprehensive guide to using .env files:
- Loading .env files
- Various value formats (strings, numbers, booleans, JSON)
- Quoted vs unquoted values
- Comments and empty lines
- Environment-specific .env files
- Creating .env.example templates

**Run it:**
```bash
python examples/dotenv_example.py
```

**Topics Covered:**
- .env file syntax and formats
- Type conversion from environment variables
- Precedence rules (existing env vars are preserved)
- Best practices for .env files

## Common Patterns

### Pattern 1: Development vs Production

```python
import os
from liteconfig_py import Config

# Determine environment
env = os.getenv('APP_ENV', 'development')

# Load environment-specific config
config = Config(
    f'config.{env}.json',
    load_dotenv=True,
    dotenv_path=f'.env.{env}'
)
```

### Pattern 2: Configuration with Validation

```python
from pydantic import BaseModel
from liteconfig_py import Config

class AppConfig(BaseModel):
    port: int
    debug: bool

config = Config('config.json')
validated = config.validate(AppConfig)

# Type-safe access
print(validated.port)  # IDE knows this is an int
```

### Pattern 3: Namespaced Configuration

```python
from liteconfig_py import Config

config = Config('config.json', env_prefix='MYAPP_')

# Only MYAPP_* environment variables will be applied
# MYAPP_DATABASE_HOST -> database.host
```

### Pattern 4: Configuration Factory

```python
from liteconfig_py import Config

def load_config(environment: str = 'development') -> Config:
    """Load configuration for the given environment."""
    return Config(
        f'config/{environment}.json',
        load_dotenv=True,
        dotenv_path=f'.env.{environment}'
    )

# Usage
config = load_config('production')
```

## Configuration File Examples

### Basic config.json

```json
{
  "app": {
    "name": "MyApp",
    "port": 8080,
    "debug": false
  },
  "database": {
    "host": "localhost",
    "port": 5432,
    "name": "myapp"
  }
}
```

### Basic config.yml

```yaml
app:
  name: MyApp
  port: 8080
  debug: false

database:
  host: localhost
  port: 5432
  name: myapp
```

### Example .env

```bash
# Application settings
APP_PORT=3000
APP_DEBUG=true

# Database
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=myapp_dev
DATABASE_USER=dev_user
DATABASE_PASSWORD=dev_password

# API Keys
API_KEY=your_api_key_here
```

### Example .env.example

```bash
# Copy this to .env and fill in your values

# Application
APP_PORT=8080
APP_DEBUG=false

# Database
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=your_database
DATABASE_USER=your_username
DATABASE_PASSWORD=your_password

# API Keys
API_KEY=get_from_api_dashboard
```

## Testing Your Configuration

Always validate your configuration on application startup:

```python
from liteconfig_py import Config, ConfigValidationError

try:
    config = Config('config.json', load_dotenv=True)

    # Validate critical values
    assert config.get('database.host'), "Database host is required"
    assert config.get('api.key'), "API key is required"

    # Or use Pydantic validation
    validated = config.validate(MyConfigSchema)

    print("✓ Configuration is valid")
except (FileNotFoundError, ConfigValidationError) as e:
    print(f"✗ Configuration error: {e}")
    exit(1)
```

## Security Best Practices

1. **Never commit secrets**
   - Add `.env` to your `.gitignore`
   - Use `.env.example` as a template
   - Commit only example/template files

2. **Use environment-specific configs**
   - Development: permissive, detailed logging
   - Staging: production-like, with extra monitoring
   - Production: strict, minimal logging

3. **Validate on startup**
   - Fail fast if configuration is invalid
   - Use Pydantic for strong validation
   - Check for required secrets

4. **Use secret management**
   - For production, use proper secret management (Vault, AWS Secrets Manager, etc.)
   - .env files are for local development only

5. **Apply principle of least privilege**
   - Only grant necessary permissions
   - Use separate credentials for different environments
   - Rotate credentials regularly

## Troubleshooting

### Issue: Environment variables not being loaded

**Solution:** Make sure you're passing `load_dotenv=True`:
```python
config = Config('config.json', load_dotenv=True)
```

### Issue: Wrong values being used

**Check:**
1. Environment variable precedence (existing env vars are not overridden by .env)
2. Correct .env file path
3. Naming conventions (APP_DATABASE_HOST -> app.database.host)

### Issue: Validation errors in production

**Solution:**
1. Check all required fields are present
2. Verify field constraints (min/max values)
3. Ensure secrets are properly loaded
4. Review validation error messages carefully

## Additional Resources

- [Main Documentation](../README.md)
- [API Reference](../README.md#usage)
- [Contributing Guide](../README.md#contributing)

## Need Help?

If you have questions or run into issues:
1. Check the examples in this directory
2. Review the main README.md
3. Open an issue on GitHub
