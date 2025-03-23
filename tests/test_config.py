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

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary config files
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # JSON config
        self.json_config_path = os.path.join(self.temp_dir.name, 'config.json')
        with open(self.json_config_path, 'w') as f:
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
            }, f)
            
        # Clear environment variables that might interfere with tests
        for env_var in list(os.environ.keys()):
            if env_var.startswith('APP_') or env_var.startswith('DATABASE_'):
                del os.environ[env_var]
                
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
        
    def test_load_json_config(self):
        """Test loading a JSON configuration file."""
        config = Config(self.json_config_path)
        
        self.assertTrue(config.get('app.debug'))
        self.assertEqual(config.get('app.port'), 8080)
        self.assertEqual(config.get('database.host'), 'localhost')
        
    def test_get_with_default(self):
        """Test getting a value with a default."""
        config = Config(self.json_config_path)
        
        self.assertEqual(config.get('nonexistent.key'), None)
        self.assertEqual(config.get('nonexistent.key', 'default'), 'default')
        
    def test_environment_variable_override(self):
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
        
    def test_environment_variable_types(self):
        """Test that environment variables are correctly typed."""
        os.environ['APP_DEBUG'] = 'false'  # Should be converted to boolean
        os.environ['APP_PORT'] = '9000'    # Should be converted to int
        os.environ['DATABASE_HOST'] = 'db.example.com'  # Should remain string
        
        config = Config(self.json_config_path)
        
        self.assertFalse(config.get('app.debug'))
        self.assertEqual(config.get('app.port'), 9000)
        self.assertEqual(config.get('database.host'), 'db.example.com')
        
    def test_dictionary_access(self):
        """Test dictionary-style access."""
        config = Config(self.json_config_path)
        
        self.assertTrue(config['app.debug'])
        self.assertEqual(config['app.port'], 8080)
        
        with self.assertRaises(KeyError):
            _ = config['nonexistent.key']
            
    def test_set_value(self):
        """Test setting a configuration value."""
        config = Config(self.json_config_path)
        
        config.set('app.debug', False)
        self.assertFalse(config.get('app.debug'))
        
        config.set('new.key', 'value')
        self.assertEqual(config.get('new.key'), 'value')
        
    def test_env_prefix(self):
        """Test using an environment variable prefix."""
        os.environ['MYAPP_APP_PORT'] = '9000'
        os.environ['APP_PORT'] = '8000'  # This should be ignored
        
        config = Config(self.json_config_path, env_prefix='MYAPP_')
        
        self.assertEqual(config.get('app.port'), 9000)
        

if __name__ == '__main__':
    unittest.main()