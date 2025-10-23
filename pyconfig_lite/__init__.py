"""
pyconfig-lite - A minimal, flexible Python configuration loader with environment variable support.
"""

from typing import List

from .config import Config

# Optional validation support
try:
    from .validation import validate_config, validate_config_section, ConfigValidationError
    __all__: List[str] = ['Config', 'validate_config', 'validate_config_section', 'ConfigValidationError']
except ImportError:
    __all__ = ['Config']

__version__: str = '0.2.0'