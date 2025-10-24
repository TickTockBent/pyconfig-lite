"""
Schema validation support for liteconfig_py using Pydantic.
"""
from typing import Any, Dict, Type, TypeVar, cast

try:
    from pydantic import BaseModel, ValidationError
    PYDANTIC_AVAILABLE = True
except ImportError:  # pragma: no cover
    PYDANTIC_AVAILABLE = False
    BaseModel = object  # noqa: F811
    ValidationError = Exception  # noqa: F811

T = TypeVar('T', bound='BaseModel')


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


def validate_config(config_data: Dict[str, Any], schema: Type[T]) -> T:
    """
    Validate configuration data against a Pydantic schema.

    Args:
        config_data: The configuration dictionary to validate
        schema: A Pydantic BaseModel class defining the expected schema

    Returns:
        An instance of the schema with validated data

    Raises:
        ConfigValidationError: If validation fails
        ImportError: If Pydantic is not installed

    Example:
        ```python
        from pydantic import BaseModel
        from liteconfig_py import Config
        from liteconfig_py.validation import validate_config

        class AppConfig(BaseModel):
            debug: bool
            port: int

        config = Config('config.json')
        validated = validate_config(config.get_all(), AppConfig)
        print(validated.port)  # Type-safe access
        ```
    """
    if not PYDANTIC_AVAILABLE:
        raise ImportError(
            "Pydantic is required for schema validation. "
            "Install it with: pip install pydantic>=2.0"
        )

    try:
        return schema(**config_data)  # type: ignore[no-any-return]
    except ValidationError as e:
        raise ConfigValidationError(f"Configuration validation failed: {e}") from e


def validate_config_section(
    config_data: Dict[str, Any],
    section: str,
    schema: Type[T]
) -> T:
    """
    Validate a specific section of configuration data.

    Args:
        config_data: The full configuration dictionary
        section: The section key to validate (e.g., 'database', 'app')
        schema: A Pydantic BaseModel class defining the expected schema

    Returns:
        An instance of the schema with validated section data

    Raises:
        ConfigValidationError: If validation fails or section not found
        ImportError: If Pydantic is not installed

    Example:
        ```python
        from pydantic import BaseModel
        from liteconfig_py import Config
        from liteconfig_py.validation import validate_config_section

        class DatabaseConfig(BaseModel):
            host: str
            port: int
            user: str

        config = Config('config.json')
        db_config = validate_config_section(config.get_all(), 'database', DatabaseConfig)
        ```
    """
    if section not in config_data:
        raise ConfigValidationError(f"Configuration section '{section}' not found")

    section_data = config_data[section]
    if not isinstance(section_data, dict):
        raise ConfigValidationError(
            f"Configuration section '{section}' is not a dictionary"
        )

    return validate_config(cast(Dict[str, Any], section_data), schema)
