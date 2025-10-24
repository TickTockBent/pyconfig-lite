"""
Basic usage example for liteconfig_py.
"""
import os
import json
from liteconfig_py import Config

# Create example configuration files
def create_example_configs():
    # Example YAML config
    with open('config.yml', 'w') as f:
        f.write("""
app:
  debug: true
  port: 8080
database:
  host: localhost
  user: user123
  password: pass123
        """)
    
    # Example JSON config
    with open('config.json', 'w') as f:
        json.dump({
            "app": {
                "debug": True,
                "port": 8080
            },
            "database": {
                "host": "localhost",
                "user": "user123",
                "password": "pass123"
            }
        }, f, indent=2)

# Create the example files
create_example_configs()

# Basic usage
print("\n=== Basic Usage ===")
config = Config('config.yml')
print(f"App debug mode: {config.get('app.debug')}")
print(f"Database host: {config.get('database.host')}")
print(f"App port: {config.get('app.port')}")

# Using default values
print("\n=== Default Values ===")
print(f"Nonexistent key with default: {config.get('nonexistent.key', default='default_value')}")

# Environment variable overrides
print("\n=== Environment Variable Overrides ===")
os.environ['DATABASE_HOST'] = 'db.production.com'
os.environ['APP_PORT'] = '80'

# Create a new config instance to pick up the environment variables
config = Config('config.yml')
print(f"Database host (from env): {config.get('database.host')}")
print(f"App port (from env): {config.get('app.port')}")

# Using JSON config
print("\n=== JSON Config ===")
config_json = Config('config.json')
print(f"JSON config - App debug mode: {config_json.get('app.debug')}")
print(f"JSON config - Database host: {config_json.get('database.host')}")

# Dictionary-style access
print("\n=== Dictionary-style Access ===")
try:
    print(f"App debug mode: {config['app.debug']}")
    print(f"Nonexistent key: {config['nonexistent.key']}")
except KeyError as e:
    print(f"KeyError: {e}")

# Clean up example files
import os
os.remove('config.yml')
os.remove('config.json')