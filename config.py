"""
pyconfig-lite - A minimal, flexible Python configuration loader with environment variable support.
"""
import os
import json
import importlib.util


class Config:
    """
    A simple configuration manager that loads from YAML, JSON, or TOML files
    and supports environment variable overrides.
    """

    def __init__(self, config_file, env_prefix=None):
        """
        Initialize the configuration loader.

        Args:
            config_file (str): Path to the configuration file (YAML, JSON, or TOML)
            env_prefix (str, optional): Prefix for environment variables. If None,
                                       no prefix is used. Defaults to None.
        """
        self.config_file = config_file
        self.env_prefix = env_prefix
        self.config_data = {}
        
        # Load the configuration file
        self._load_config()
        
        # Override with environment variables
        self._apply_env_overrides()

    def _load_config(self):
        """Load configuration from file based on file extension."""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")

        file_ext = os.path.splitext(self.config_file)[1].lower()
        
        try:
            if file_ext in ('.yaml', '.yml'):
                self._load_yaml()
            elif file_ext == '.json':
                self._load_json()
            elif file_ext == '.toml':
                self._load_toml()
            else:
                raise ValueError(f"Unsupported configuration format: {file_ext}")
        except Exception as e:
            raise ValueError(f"Error loading configuration: {str(e)}")

    def _load_yaml(self):
        """Load configuration from YAML file."""
        try:
            # Check if PyYAML is available
            if importlib.util.find_spec("yaml") is None:
                raise ImportError("PyYAML is required for YAML configuration files. "
                                 "Install it with: pip install PyYAML")
            
            import yaml
            with open(self.config_file, 'r') as f:
                self.config_data = yaml.safe_load(f)
        except ImportError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Failed to parse YAML file: {str(e)}")

    def _load_json(self):
        """Load configuration from JSON file."""
        try:
            with open(self.config_file, 'r') as f:
                self.config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON file: {str(e)}")

    def _load_toml(self):
        """Load configuration from TOML file."""
        try:
            # Check if toml is available
            if importlib.util.find_spec("toml") is None:
                raise ImportError("toml is required for TOML configuration files. "
                                 "Install it with: pip install toml")
            
            import toml
            with open(self.config_file, 'r') as f:
                self.config_data = toml.load(f)
        except ImportError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Failed to parse TOML file: {str(e)}")

    def _apply_env_overrides(self):
        """Override configuration values with matching environment variables."""
        for env_name, env_value in os.environ.items():
            if self.env_prefix and not env_name.startswith(self.env_prefix):
                continue
                
            # Remove prefix if it exists
            if self.env_prefix:
                config_key = env_name[len(self.env_prefix):]
            else:
                config_key = env_name
                
            # Convert environment variable name to configuration key path
            # e.g., DATABASE_HOST -> database.host
            config_path = config_key.lower().replace('__', '.').replace('_', '.')
            
            # If the environment value exists and the configuration key exists,
            # override the value
            if config_path:
                # Try to convert the environment value to appropriate Python type
                try:
                    # Try to parse as JSON first (for booleans, numbers, lists, etc.)
                    parsed_value = json.loads(env_value)
                except json.JSONDecodeError:
                    # If not valid JSON, keep as string
                    parsed_value = env_value
                    
                # Set the value in the config
                self._set_nested_value(config_path, parsed_value)

    def _set_nested_value(self, key_path, value):
        """Set a value in the nested configuration using dot notation."""
        keys = key_path.split('.')
        current = self.config_data
        
        # Navigate to the nested location
        for i, key in enumerate(keys[:-1]):
            # Create dict if it doesn't exist
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value

    def get(self, key_path, default=None):
        """
        Get a configuration value using dot notation.
        
        Args:
            key_path (str): The key path in dot notation, e.g., 'database.host'
            default: The default value to return if the key doesn't exist
            
        Returns:
            The configuration value or the default if not found
        """
        keys = key_path.split('.')
        value = self.config_data
        
        # Navigate through the nested dictionaries
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value

    def set(self, key_path, value):
        """
        Set a configuration value using dot notation.
        
        Args:
            key_path (str): The key path in dot notation, e.g., 'database.host'
            value: The value to set
        """
        self._set_nested_value(key_path, value)

    def __getitem__(self, key_path):
        """
        Allow dictionary-style access to configuration values.
        
        Args:
            key_path (str): The key path in dot notation, e.g., 'database.host'
            
        Returns:
            The configuration value
            
        Raises:
            KeyError: If the key doesn't exist
        """
        value = self.get(key_path)
        if value is None:
            raise KeyError(f"Configuration key not found: {key_path}")
        return value

    def get_all(self):
        """
        Get all configuration values.
        
        Returns:
            dict: The entire configuration dictionary
        """
        return self.config_data