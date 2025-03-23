# pyconfig-lite

*A minimal, flexible Python configuration loader with environment variable support.*

## Overview

**pyconfig-lite** is a simple Python library designed to streamline configuration management for Python applications, CLI tools, scripts, and services. It allows loading configuration from YAML, JSON, or TOML files, and automatically integrates environment variables to override configuration values, offering flexibility across different deployment environments.

## Features

* **Flexible Format Support:** YAML, JSON, TOML.
* **Environment Overrides:** Automatic merging of environment variables.
* **Nested Configurations:** Supports nested configuration retrieval via dot notation.
* **Minimal Dependencies:** Lightweight and efficient.
* **Simple API:** Easy-to-use interface with intuitive methods.

## Installation

```bash
pip install pyconfig-lite
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
from pyconfig_lite import Config

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
from pyconfig_lite import Config

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

## Potential Enhancements

* Configuration schema validation
* Integration with `.env` files
* Auto-reload configuration upon file changes

## Why pyconfig-lite?

* Simplifies common configuration tasks
* Enhances portability and adaptability between environments
* Easy integration into existing projects
* Lightweight with minimal dependencies

## Contributing

Contributions are welcome! Please submit issues, improvements, or pull requests on GitHub.

## License

MIT License. See `LICENSE` for details.