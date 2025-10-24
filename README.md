# liteconfig_py

[![CI](https://github.com/TickTockBent/liteconfig_py/actions/workflows/ci.yml/badge.svg)](https://github.com/TickTockBent/liteconfig_py/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/TickTockBent/liteconfig_py/branch/main/graph/badge.svg)](https://codecov.io/gh/TickTockBent/liteconfig_py)
[![Python Version](https://img.shields.io/pypi/pyversions/liteconfig_py)](https://pypi.org/project/liteconfig_py/)
[![PyPI version](https://badge.fury.io/py/liteconfig_py.svg)](https://badge.fury.io/py/liteconfig_py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

*A minimal, flexible Python configuration loader with environment variable support.*

## Overview

**liteconfig_py** is a simple Python library designed to streamline configuration management for Python applications, CLI tools, scripts, and services. It allows loading configuration from YAML, JSON, or TOML files, and automatically integrates environment variables to override configuration values, offering flexibility across different deployment environments.

## Features

* **Flexible Format Support:** YAML, JSON, TOML.
* **Environment Overrides:** Automatic merging of environment variables.
* **Nested Configurations:** Supports nested configuration retrieval via dot notation.
* **Schema Validation:** Optional Pydantic integration for type-safe configuration.
* **Type Hints:** Full type annotation support for better IDE experience.
* **Minimal Dependencies:** Lightweight and efficient.
* **Simple API:** Easy-to-use interface with intuitive methods.
* **95%+ Test Coverage:** Comprehensive test suite ensuring reliability.

## Installation

```bash
pip install liteconfig_py
```

* Optional dependencies:

```bash
pip install PyYAML toml
```

## Usage

### Basic Example

**Configuration file:** `config.yml`

```yaml
app:
  debug: true
  port: 8080
database:
  host: localhost
  user: user123
  password: pass123
```

**Python script:** `main.py`

```python
from liteconfig_py import Config

config = Config('config.yml')

print(config.get('app.debug'))  # True
print(config.get('database.host'))  # 'localhost'
```

### Overriding Values with Environment Variables

Environment variables automatically override file values if they match the configuration keys:

```bash
export DATABASE_HOST='db.production.com'
export APP_PORT=80
```

**Python script:**

```python
from liteconfig_py import Config

config = Config('config.yml')

print(config.get('database.host'))  # 'db.production.com'
print(config.get('app.port'))  # 80
```

### Advanced Usage

#### Default Values

```python
config.get('nonexistent.key', default='default_value')
```

#### Loading Different Formats

* **JSON:**

```python
config = Config('config.json')
```

* **TOML:**

```python
config = Config('config.toml')
```

#### Using Environment Variable Prefix

If you want to limit which environment variables can override your configuration, you can specify a prefix:

```python
config = Config('config.yml', env_prefix='MYAPP_')
```

This will only consider environment variables that start with `MYAPP_`, like `MYAPP_DATABASE_HOST`.

#### Loading from .env Files

Load environment variables from .env files for local development:

```python
from liteconfig_py import Config

# Load config and .env file
config = Config('config.yml', load_dotenv=True, dotenv_path='.env')

# Or use default .env location
config = Config('config.yml', load_dotenv=True)
```

Example `.env` file:

```bash
# Database configuration
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=dev_user
DATABASE_PASSWORD=dev_pass123

# Application settings
APP_DEBUG=true
APP_PORT=8080
```

**Note:** Existing environment variables take precedence over .env file values.

#### Schema Validation with Pydantic

For type-safe configuration with validation, you can use Pydantic models:

```python
from pydantic import BaseModel, Field
from liteconfig_py import Config

class DatabaseConfig(BaseModel):
    host: str
    port: int = Field(ge=1, le=65535)
    user: str
    password: str

class AppConfig(BaseModel):
    debug: bool = False
    port: int = 8080

config = Config('config.yml')

# Validate entire config
app_config = config.validate_section('app', AppConfig)
print(app_config.debug)  # Type-safe access with validation

# Validate specific section
db_config = config.validate_section('database', DatabaseConfig)
print(db_config.host)  # Guaranteed to be a string
```

Install with validation support:
```bash
pip install liteconfig_py[validation]
```

## Examples

Check out the [examples directory](examples/) for comprehensive demonstrations:

- **[basic_usage.py](examples/basic_usage.py)** - Getting started with configuration loading
- **[validation_example.py](examples/validation_example.py)** - Schema validation with Pydantic
- **[multi_env_example.py](examples/multi_env_example.py)** - Managing multiple environments
- **[production_setup.py](examples/production_setup.py)** - Production-ready configuration
- **[dotenv_example.py](examples/dotenv_example.py)** - Working with .env files

See the [examples README](examples/README.md) for detailed information.

## Potential Enhancements

* Auto-reload configuration upon file changes
* Config file watching and hot-reloading
* Config encryption/decryption support

## Why liteconfig_py?

* Simplifies common configuration tasks
* Enhances portability and adaptability between environments
* Easy integration into existing projects
* Lightweight with minimal dependencies

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes and releases.

## Contributing

Contributions are welcome! Please submit issues, improvements, or pull requests on GitHub.

## License

MIT License. See `LICENSE` for details.