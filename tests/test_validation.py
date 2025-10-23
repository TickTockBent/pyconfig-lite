"""
Tests for validation functionality.
"""
import os
import json
import tempfile
import unittest
from pyconfig_lite import Config

try:
    from pydantic import BaseModel, Field, ValidationError
    from pyconfig_lite.validation import (
        validate_config,
        validate_config_section,
        ConfigValidationError
    )
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


@unittest.skipIf(not PYDANTIC_AVAILABLE, "Pydantic not installed")
class TestValidation(unittest.TestCase):
    """Test cases for configuration validation."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()

        # Store original environment and clear test-related vars
        self.original_env = os.environ.copy()
        for key in list(os.environ.keys()):
            if key.startswith(('APP_', 'DATABASE_', 'MYAPP_', 'FLAG', 'ITEMS', 'PORT')):
                del os.environ[key]

        # Create test config
        self.test_config_data = {
            "app": {
                "name": "TestApp",
                "debug": True,
                "port": 8080
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "user": "dbuser",
                "password": "secret"
            }
        }

        self.config_path = os.path.join(self.temp_dir.name, 'config.json')
        with open(self.config_path, 'w') as f:
            json.dump(self.test_config_data, f)

    def tearDown(self) -> None:
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_validate_full_config(self) -> None:
        """Test validating the entire configuration."""
        class FullConfig(BaseModel):
            app: dict
            database: dict

        config = Config(self.config_path)
        validated = config.validate(FullConfig)

        self.assertIsInstance(validated, FullConfig)
        self.assertEqual(validated.app, self.test_config_data["app"])
        self.assertEqual(validated.database, self.test_config_data["database"])

    def test_validate_config_section(self) -> None:
        """Test validating a specific configuration section."""
        class DatabaseConfig(BaseModel):
            host: str
            port: int
            user: str
            password: str

        config = Config(self.config_path)
        db_config = config.validate_section('database', DatabaseConfig)

        self.assertIsInstance(db_config, DatabaseConfig)
        self.assertEqual(db_config.host, "localhost")
        self.assertEqual(db_config.port, 5432)
        self.assertEqual(db_config.user, "dbuser")
        self.assertEqual(db_config.password, "secret")

    def test_validate_with_type_coercion(self) -> None:
        """Test that Pydantic coerces types appropriately."""
        class AppConfig(BaseModel):
            name: str
            debug: bool
            port: int

        config = Config(self.config_path)
        app_config = config.validate_section('app', AppConfig)

        self.assertEqual(app_config.name, "TestApp")
        self.assertTrue(app_config.debug)
        self.assertEqual(app_config.port, 8080)

    def test_validate_with_defaults(self) -> None:
        """Test validation with default values."""
        class AppConfig(BaseModel):
            name: str
            debug: bool = False
            port: int = 3000
            timeout: int = 30

        minimal_config = {"app": {"name": "MinimalApp"}}
        minimal_path = os.path.join(self.temp_dir.name, 'minimal.json')
        with open(minimal_path, 'w') as f:
            json.dump(minimal_config, f)

        config = Config(minimal_path)
        app_config = config.validate_section('app', AppConfig)

        self.assertEqual(app_config.name, "MinimalApp")
        self.assertFalse(app_config.debug)
        self.assertEqual(app_config.port, 3000)
        self.assertEqual(app_config.timeout, 30)

    def test_validate_with_field_constraints(self) -> None:
        """Test validation with Pydantic field constraints."""
        class StrictConfig(BaseModel):
            port: int = Field(ge=1, le=65535)
            name: str = Field(min_length=1, max_length=50)

        valid_config = {"port": 8080, "name": "ValidName"}
        valid_path = os.path.join(self.temp_dir.name, 'valid.json')
        with open(valid_path, 'w') as f:
            json.dump(valid_config, f)

        config = Config(valid_path)
        validated = config.validate(StrictConfig)
        self.assertEqual(validated.port, 8080)

    def test_validate_fails_on_invalid_type(self) -> None:
        """Test that validation fails with incorrect types."""
        class StrictConfig(BaseModel):
            port: int
            enabled: bool

        invalid_config = {"port": "not-a-number", "enabled": "yes"}
        invalid_path = os.path.join(self.temp_dir.name, 'invalid_type.json')
        with open(invalid_path, 'w') as f:
            json.dump(invalid_config, f)

        config = Config(invalid_path)
        with self.assertRaises(ConfigValidationError):
            config.validate(StrictConfig)

    def test_validate_fails_on_missing_required_field(self) -> None:
        """Test that validation fails when required fields are missing."""
        class RequiredConfig(BaseModel):
            required_field: str
            optional_field: str = "default"

        incomplete_config = {"optional_field": "present"}
        incomplete_path = os.path.join(self.temp_dir.name, 'incomplete.json')
        with open(incomplete_path, 'w') as f:
            json.dump(incomplete_config, f)

        config = Config(incomplete_path)
        with self.assertRaises(ConfigValidationError):
            config.validate(RequiredConfig)

    def test_validate_section_not_found(self) -> None:
        """Test validation when section doesn't exist."""
        class AnyConfig(BaseModel):
            value: str

        config = Config(self.config_path)
        with self.assertRaises(ConfigValidationError) as context:
            config.validate_section('nonexistent', AnyConfig)
        self.assertIn("not found", str(context.exception))

    def test_validate_section_not_dict(self) -> None:
        """Test validation when section is not a dictionary."""
        scalar_config = {"scalar": "value"}
        scalar_path = os.path.join(self.temp_dir.name, 'scalar.json')
        with open(scalar_path, 'w') as f:
            json.dump(scalar_config, f)

        class AnyConfig(BaseModel):
            field: str

        config = Config(scalar_path)
        with self.assertRaises(ConfigValidationError) as context:
            config.validate_section('scalar', AnyConfig)
        self.assertIn("not a dictionary", str(context.exception))

    def test_validate_with_nested_models(self) -> None:
        """Test validation with nested Pydantic models."""
        class DatabaseConfig(BaseModel):
            host: str
            port: int
            user: str
            password: str

        class AppConfig(BaseModel):
            name: str
            debug: bool
            port: int

        class FullConfig(BaseModel):
            app: AppConfig
            database: DatabaseConfig

        config = Config(self.config_path)
        validated = config.validate(FullConfig)

        self.assertIsInstance(validated.app, AppConfig)
        self.assertIsInstance(validated.database, DatabaseConfig)
        self.assertEqual(validated.database.host, "localhost")
        self.assertEqual(validated.app.name, "TestApp")

    def test_validate_with_env_overrides(self) -> None:
        """Test that validation works with environment variable overrides."""
        class AppConfig(BaseModel):
            name: str
            debug: bool
            port: int

        os.environ['APP_PORT'] = '9999'

        config = Config(self.config_path)
        app_config = config.validate_section('app', AppConfig)

        # Environment override should be reflected in validated config
        self.assertEqual(app_config.port, 9999)

    def test_standalone_validate_config(self) -> None:
        """Test using validate_config function directly."""
        class SimpleConfig(BaseModel):
            key: str

        data = {"key": "value"}
        validated = validate_config(data, SimpleConfig)

        self.assertIsInstance(validated, SimpleConfig)
        self.assertEqual(validated.key, "value")

    def test_standalone_validate_config_section(self) -> None:
        """Test using validate_config_section function directly."""
        class SectionConfig(BaseModel):
            field: str

        data = {"section": {"field": "value"}}
        validated = validate_config_section(data, 'section', SectionConfig)

        self.assertIsInstance(validated, SectionConfig)
        self.assertEqual(validated.field, "value")


class TestValidationWithoutPydantic(unittest.TestCase):
    """Test that validation gracefully fails without Pydantic."""

    def test_import_error_without_pydantic(self) -> None:
        """Test that appropriate error is raised when Pydantic is not available."""
        # This test will be skipped if Pydantic is available
        if PYDANTIC_AVAILABLE:
            self.skipTest("Pydantic is installed")

        # If we reach here, Pydantic is not installed
        # Just verify the module doesn't crash on import
        try:
            from pyconfig_lite import validation
            self.assertIsNotNone(validation)
        except ImportError:
            self.fail("Validation module should be importable even without Pydantic")


if __name__ == '__main__':
    unittest.main()
