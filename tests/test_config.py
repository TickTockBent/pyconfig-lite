"""
Tests for pyconfig_lite package.
"""
import os
import json
import tempfile
import unittest
from pyconfig_lite import Config


class TestConfig(unittest.TestCase):
    """Test cases for Config class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Create temporary config files
        self.temp_dir = tempfile.TemporaryDirectory()

        # Test data structure
        self.test_config_data = {
            "app": {
                "debug": True,
                "port": 8080
            },
            "database": {
                "host": "localhost",
                "user": "user123",
                "password": "pass123"
            }
        }

        # JSON config
        self.json_config_path = os.path.join(self.temp_dir.name, 'config.json')
        with open(self.json_config_path, 'w') as f:
            json.dump(self.test_config_data, f)

        # YAML config
        self.yaml_config_path = os.path.join(self.temp_dir.name, 'config.yml')
        try:
            import yaml
            with open(self.yaml_config_path, 'w') as f:
                yaml.dump(self.test_config_data, f)
        except ImportError:
            pass  # YAML tests will be skipped if PyYAML not installed

        # TOML config
        self.toml_config_path = os.path.join(self.temp_dir.name, 'config.toml')
        try:
            import toml
            with open(self.toml_config_path, 'w') as f:
                toml.dump(self.test_config_data, f)
        except ImportError:
            pass  # TOML tests will be skipped if toml not installed
            
        # Clear environment variables that might interfere with tests
        for env_var in list(os.environ.keys()):
            if env_var.startswith('APP_') or env_var.startswith('DATABASE_'):
                del os.environ[env_var]
                
    def tearDown(self) -> None:
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
        
    def test_load_json_config(self) -> None:
        """Test loading a JSON configuration file."""
        config = Config(self.json_config_path)
        
        self.assertTrue(config.get('app.debug'))
        self.assertEqual(config.get('app.port'), 8080)
        self.assertEqual(config.get('database.host'), 'localhost')
        
    def test_get_with_default(self) -> None:
        """Test getting a value with a default."""
        config = Config(self.json_config_path)
        
        self.assertEqual(config.get('nonexistent.key'), None)
        self.assertEqual(config.get('nonexistent.key', 'default'), 'default')
        
    def test_environment_variable_override(self) -> None:
        """Test that environment variables override config values."""
        # Set environment variables
        os.environ['APP_PORT'] = '9000'
        os.environ['DATABASE_HOST'] = 'db.example.com'
        
        config = Config(self.json_config_path)
        
        # Check that environment variables override config values
        self.assertEqual(config.get('app.port'), 9000)  # Note: converted to int
        self.assertEqual(config.get('database.host'), 'db.example.com')
        
        # Check that unset variables remain unchanged
        self.assertTrue(config.get('app.debug'))
        
    def test_environment_variable_types(self) -> None:
        """Test that environment variables are correctly typed."""
        os.environ['APP_DEBUG'] = 'false'  # Should be converted to boolean
        os.environ['APP_PORT'] = '9000'    # Should be converted to int
        os.environ['DATABASE_HOST'] = 'db.example.com'  # Should remain string
        
        config = Config(self.json_config_path)
        
        self.assertFalse(config.get('app.debug'))
        self.assertEqual(config.get('app.port'), 9000)
        self.assertEqual(config.get('database.host'), 'db.example.com')
        
    def test_dictionary_access(self) -> None:
        """Test dictionary-style access."""
        config = Config(self.json_config_path)
        
        self.assertTrue(config['app.debug'])
        self.assertEqual(config['app.port'], 8080)
        
        with self.assertRaises(KeyError):
            _ = config['nonexistent.key']
            
    def test_set_value(self) -> None:
        """Test setting a configuration value."""
        config = Config(self.json_config_path)
        
        config.set('app.debug', False)
        self.assertFalse(config.get('app.debug'))
        
        config.set('new.key', 'value')
        self.assertEqual(config.get('new.key'), 'value')
        
    def test_env_prefix(self) -> None:
        """Test using an environment variable prefix."""
        os.environ['MYAPP_APP_PORT'] = '9000'
        os.environ['APP_PORT'] = '8000'  # This should be ignored

        config = Config(self.json_config_path, env_prefix='MYAPP_')

        self.assertEqual(config.get('app.port'), 9000)

    def test_load_yaml_config(self) -> None:
        """Test loading a YAML configuration file."""
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")

        config = Config(self.yaml_config_path)

        self.assertTrue(config.get('app.debug'))
        self.assertEqual(config.get('app.port'), 8080)
        self.assertEqual(config.get('database.host'), 'localhost')

    def test_load_toml_config(self) -> None:
        """Test loading a TOML configuration file."""
        try:
            import toml
        except ImportError:
            self.skipTest("toml not installed")

        config = Config(self.toml_config_path)

        self.assertTrue(config.get('app.debug'))
        self.assertEqual(config.get('app.port'), 8080)
        self.assertEqual(config.get('database.host'), 'localhost')

    def test_yaml_with_env_override(self) -> None:
        """Test YAML config with environment variable override."""
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")

        os.environ['APP_PORT'] = '9000'
        config = Config(self.yaml_config_path)

        self.assertEqual(config.get('app.port'), 9000)

    def test_toml_with_env_override(self) -> None:
        """Test TOML config with environment variable override."""
        try:
            import toml
        except ImportError:
            self.skipTest("toml not installed")

        os.environ['DATABASE_HOST'] = 'toml.example.com'
        config = Config(self.toml_config_path)

        self.assertEqual(config.get('database.host'), 'toml.example.com')

    def test_unsupported_file_format(self) -> None:
        """Test loading an unsupported file format."""
        unsupported_path = os.path.join(self.temp_dir.name, 'config.txt')
        with open(unsupported_path, 'w') as f:
            f.write('test')

        with self.assertRaises(ValueError) as context:
            Config(unsupported_path)
        self.assertIn('Unsupported configuration format', str(context.exception))

    def test_missing_file(self) -> None:
        """Test loading a non-existent file."""
        with self.assertRaises(FileNotFoundError):
            Config('/nonexistent/path/config.json')

    def test_deeply_nested_config(self) -> None:
        """Test deeply nested configuration structures."""
        nested_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "value": "deep"
                        }
                    }
                }
            }
        }
        nested_path = os.path.join(self.temp_dir.name, 'nested.json')
        with open(nested_path, 'w') as f:
            json.dump(nested_data, f)

        config = Config(nested_path)
        self.assertEqual(config.get('level1.level2.level3.level4.value'), 'deep')

    def test_deeply_nested_env_override(self) -> None:
        """Test environment override for deeply nested keys."""
        nested_data = {
            "app": {
                "server": {
                    "settings": {
                        "port": 8080
                    }
                }
            }
        }
        nested_path = os.path.join(self.temp_dir.name, 'nested_env.json')
        with open(nested_path, 'w') as f:
            json.dump(nested_data, f)

        os.environ['APP_SERVER_SETTINGS_PORT'] = '9090'
        config = Config(nested_path)
        self.assertEqual(config.get('app.server.settings.port'), 9090)

    def test_empty_config_file(self) -> None:
        """Test loading an empty JSON configuration file with prefix to avoid env pollution."""
        empty_path = os.path.join(self.temp_dir.name, 'empty.json')
        with open(empty_path, 'w') as f:
            f.write('{}')

        # Use a prefix to prevent system env vars from being added
        config = Config(empty_path, env_prefix='TESTPREFIX_')
        self.assertEqual(config.get_all(), {})
        self.assertIsNone(config.get('any.key'))

    def test_array_values_in_config(self) -> None:
        """Test configuration with array values."""
        array_data = {
            "servers": ["host1", "host2", "host3"],
            "ports": [8080, 8081, 8082]
        }
        array_path = os.path.join(self.temp_dir.name, 'array.json')
        with open(array_path, 'w') as f:
            json.dump(array_data, f)

        config = Config(array_path)
        self.assertEqual(config.get('servers'), ["host1", "host2", "host3"])
        self.assertEqual(config.get('ports'), [8080, 8081, 8082])

    def test_array_env_override(self) -> None:
        """Test environment override with JSON array."""
        array_data = {"items": [1, 2, 3]}
        array_path = os.path.join(self.temp_dir.name, 'array_env.json')
        with open(array_path, 'w') as f:
            json.dump(array_data, f)

        os.environ['ITEMS'] = '["a", "b", "c"]'
        config = Config(array_path)
        self.assertEqual(config.get('items'), ["a", "b", "c"])

    def test_null_values(self) -> None:
        """Test handling of null/None values."""
        null_data = {
            "value": None,
            "nested": {
                "nullable": None
            }
        }
        null_path = os.path.join(self.temp_dir.name, 'null.json')
        with open(null_path, 'w') as f:
            json.dump(null_data, f)

        config = Config(null_path)
        self.assertIsNone(config.get('value'))
        self.assertIsNone(config.get('nested.nullable'))

    def test_special_characters_in_values(self) -> None:
        """Test configuration with special characters."""
        special_data = {
            "password": "p@$$w0rd!#&*",
            "url": "https://example.com/path?query=value&other=123"
        }
        special_path = os.path.join(self.temp_dir.name, 'special.json')
        with open(special_path, 'w') as f:
            json.dump(special_data, f)

        config = Config(special_path)
        self.assertEqual(config.get('password'), "p@$$w0rd!#&*")
        self.assertEqual(config.get('url'), "https://example.com/path?query=value&other=123")

    def test_numeric_string_values(self) -> None:
        """Test that numeric strings remain strings unless from env."""
        numeric_data = {
            "code": "12345",
            "zip": "90210"
        }
        numeric_path = os.path.join(self.temp_dir.name, 'numeric.json')
        with open(numeric_path, 'w') as f:
            json.dump(numeric_data, f)

        # Use prefix to avoid env var interference
        config = Config(numeric_path, env_prefix='NUMERIC_TEST_')
        self.assertEqual(config.get('code'), "12345")
        self.assertIsInstance(config.get('code'), str)

    def test_boolean_string_conversion(self) -> None:
        """Test conversion of boolean-like strings from env vars."""
        bool_data = {"flag": True}
        bool_path = os.path.join(self.temp_dir.name, 'bool.json')

        # JSON parsing only works with lowercase 'true'/'false'
        test_cases = [
            ('true', True),
            ('false', False),
            ('1', 1),  # Numbers are parsed
            ('0', 0),
        ]

        for env_value, expected in test_cases:
            # Create fresh config file for each test case
            with open(bool_path, 'w') as f:
                json.dump(bool_data, f)

            os.environ['FLAG'] = env_value
            config = Config(bool_path)
            self.assertEqual(config.get('flag'), expected)
            del os.environ['FLAG']

        # Test that uppercase True/False remain as strings (not valid JSON)
        with open(bool_path, 'w') as f:
            json.dump(bool_data, f)
        os.environ['FLAG'] = 'True'
        config = Config(bool_path)
        self.assertEqual(config.get('flag'), 'True')  # Remains string
        del os.environ['FLAG']

    def test_set_creates_nested_structure(self) -> None:
        """Test that set() creates nested dictionaries as needed."""
        config = Config(self.json_config_path)

        config.set('new.deeply.nested.value', 'test')
        self.assertEqual(config.get('new.deeply.nested.value'), 'test')

    def test_set_overwrites_non_dict_values(self) -> None:
        """Test that set() overwrites non-dict intermediate values."""
        config = Config(self.json_config_path)

        # First set a scalar value
        config.set('path.value', 'scalar')
        self.assertEqual(config.get('path.value'), 'scalar')

        # Now set a nested value under the same path
        config.set('path.value.nested', 'new')
        self.assertEqual(config.get('path.value.nested'), 'new')

    def test_getitem_with_none_value(self) -> None:
        """Test that __getitem__ distinguishes between None and missing keys."""
        null_data = {"existing": None}
        null_path = os.path.join(self.temp_dir.name, 'null_getitem.json')
        with open(null_path, 'w') as f:
            json.dump(null_data, f)

        config = Config(null_path)

        # Existing key with None value should raise KeyError
        with self.assertRaises(KeyError):
            _ = config['existing']

        # Non-existing key should also raise KeyError
        with self.assertRaises(KeyError):
            _ = config['nonexistent']

    def test_complex_json_types(self) -> None:
        """Test configuration with complex nested JSON structures."""
        complex_data = {
            "mixed": {
                "string": "value",
                "number": 42,
                "float": 3.14,
                "bool": True,
                "null": None,
                "array": [1, "two", 3.0, True, None],
                "nested": {
                    "deep": {
                        "deeper": "value"
                    }
                }
            }
        }
        complex_path = os.path.join(self.temp_dir.name, 'complex.json')
        with open(complex_path, 'w') as f:
            json.dump(complex_data, f)

        config = Config(complex_path)
        self.assertEqual(config.get('mixed.string'), "value")
        self.assertEqual(config.get('mixed.number'), 42)
        self.assertAlmostEqual(config.get('mixed.float'), 3.14)
        self.assertEqual(config.get('mixed.bool'), True)
        self.assertIsNone(config.get('mixed.null'))
        self.assertEqual(config.get('mixed.array'), [1, "two", 3.0, True, None])
        self.assertEqual(config.get('mixed.nested.deep.deeper'), "value")

    def test_invalid_json_file(self) -> None:
        """Test loading a malformed JSON file."""
        invalid_path = os.path.join(self.temp_dir.name, 'invalid.json')
        with open(invalid_path, 'w') as f:
            f.write('{invalid json content')

        with self.assertRaises(ValueError) as context:
            Config(invalid_path)
        self.assertIn('Failed to parse JSON file', str(context.exception))

    def test_env_prefix_case_sensitivity(self) -> None:
        """Test that environment prefix matching is case-sensitive."""
        os.environ['MYAPP_PORT'] = '9000'
        os.environ['myapp_PORT'] = '8000'

        config = Config(self.json_config_path, env_prefix='MYAPP_')

        # Only MYAPP_ prefix should be recognized
        self.assertEqual(config.get('port'), 9000)

    def test_load_dotenv_file(self) -> None:
        """Test loading environment variables from .env file."""
        # Create a .env file
        dotenv_path = os.path.join(self.temp_dir.name, 'test.env')
        with open(dotenv_path, 'w') as f:
            f.write('DATABASE_HOST=env.example.com\n')
            f.write('APP_DEBUG=true\n')
            f.write('APP_PORT=9999\n')

        # Make sure these aren't already in environment
        for key in ['DATABASE_HOST', 'APP_DEBUG']:
            if key in os.environ:
                del os.environ[key]

        config = Config(self.json_config_path, load_dotenv=True, dotenv_path=dotenv_path)

        # Values from .env should override config
        self.assertEqual(config.get('database.host'), 'env.example.com')
        self.assertTrue(config.get('app.debug'))
        self.assertEqual(config.get('app.port'), 9999)

    def test_dotenv_with_comments_and_empty_lines(self) -> None:
        """Test .env file parsing with comments and empty lines."""
        dotenv_path = os.path.join(self.temp_dir.name, 'commented.env')
        with open(dotenv_path, 'w') as f:
            f.write('# This is a comment\n')
            f.write('\n')
            f.write('DATABASE_HOST=localhost\n')
            f.write('  \n')
            f.write('# Another comment\n')
            f.write('DATABASE_PORT=5432\n')

        for key in ['DATABASE_HOST', 'DATABASE_PORT']:
            if key in os.environ:
                del os.environ[key]

        config = Config(self.json_config_path, load_dotenv=True, dotenv_path=dotenv_path)

        self.assertEqual(config.get('database.host'), 'localhost')
        self.assertEqual(config.get('database.port'), 5432)

    def test_dotenv_with_quoted_values(self) -> None:
        """Test .env file with quoted values."""
        dotenv_path = os.path.join(self.temp_dir.name, 'quoted.env')
        with open(dotenv_path, 'w') as f:
            f.write('SINGLE_QUOTED=\'single value\'\n')
            f.write('DOUBLE_QUOTED="double value"\n')
            f.write('UNQUOTED=unquoted value\n')

        for key in ['SINGLE_QUOTED', 'DOUBLE_QUOTED', 'UNQUOTED']:
            if key in os.environ:
                del os.environ[key]

        Config(self.json_config_path, load_dotenv=True, dotenv_path=dotenv_path)

        self.assertEqual(os.environ['SINGLE_QUOTED'], 'single value')
        self.assertEqual(os.environ['DOUBLE_QUOTED'], 'double value')
        self.assertEqual(os.environ['UNQUOTED'], 'unquoted value')

    def test_dotenv_preserves_existing_env_vars(self) -> None:
        """Test that .env doesn't override existing environment variables."""
        dotenv_path = os.path.join(self.temp_dir.name, 'preserve.env')
        with open(dotenv_path, 'w') as f:
            f.write('DATABASE_HOST=from_dotenv\n')

        # Set env var before loading .env
        os.environ['DATABASE_HOST'] = 'from_existing'

        config = Config(self.json_config_path, load_dotenv=True, dotenv_path=dotenv_path)

        # Should keep the existing value
        self.assertEqual(config.get('database.host'), 'from_existing')

    def test_dotenv_missing_file(self) -> None:
        """Test that missing .env file doesn't cause error."""
        # Should not raise an error
        config = Config(self.json_config_path, load_dotenv=True, dotenv_path='/nonexistent/.env')
        self.assertIsNotNone(config)

    def test_dotenv_with_equals_in_value(self) -> None:
        """Test .env file with equals sign in value."""
        dotenv_path = os.path.join(self.temp_dir.name, 'equals.env')
        with open(dotenv_path, 'w') as f:
            f.write('CONNECTION_STRING=server=localhost;user=admin\n')

        if 'CONNECTION_STRING' in os.environ:
            del os.environ['CONNECTION_STRING']

        Config(self.json_config_path, load_dotenv=True, dotenv_path=dotenv_path)

        self.assertEqual(os.environ['CONNECTION_STRING'], 'server=localhost;user=admin')


if __name__ == '__main__':
    unittest.main()