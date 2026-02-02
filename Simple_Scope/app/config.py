"""
Configuration management for the application
"""

from dataclasses import dataclass, field, asdict
import json
import logging
import re
from pathlib import Path
from typing import Any

from app.version import __version__

# Use SimpleScope namespace to integrate with app's logging hierarchy
logger = logging.getLogger("SimpleScope.config")


def _default_save_directory() -> str:
    return str(Path.home() / "Pictures" / "scope_capture")


@dataclass
class AppConfig:
    """Configuration manager for the application"""

    # Persisted config fields
    save_directory: str = field(default_factory=_default_save_directory)
    default_filename: str = "capture"
    filename: str | None = None
    file_format: str = "png"
    background_color: str = "white"
    save_waveform: bool = False
    auto_increment: bool = False
    datestamp: bool = True
    last_used_metadata: dict = field(default_factory=dict)
    recent_directories: list = field(default_factory=list)
    display_captured_image: str = "Disabled"  # "Disabled", "Display To The Right", "Display Below"
    display_image_size: str = "Medium"  # "Small" (500), "Medium" (750), "Large" (1024)
    auto_copy_to_clipboard: bool = False
    last_connected_scope: dict = field(default_factory=dict)

    # Non-persisted fields (excluded from JSON)
    _config_file: Path = field(default=None, repr=False, compare=False)
    _app_data_dir: Path = field(default=None, repr=False, compare=False)
    _loading: bool = field(default=True, repr=False, compare=False)
    _logger: logging.Logger = field(default=None, repr=False, compare=False)

    def __post_init__(self):
        """Initialize paths and load existing config"""
        object.__setattr__(self, '_app_data_dir', Path.home() / ".simple_scope")

        if self._config_file is None:
            object.__setattr__(self, '_config_file', self._app_data_dir / "config.json")

        self._load_config()
        object.__setattr__(self, '_loading', False)

    def __setattr__(self, name: str, value: Any) -> None:
        """Custom setattr to handle auto-save and mutual exclusivity"""
        # Use object.__setattr__ for private fields to avoid recursion
        if name.startswith('_'):
            object.__setattr__(self, name, value)
            return

        # Handle mutual exclusivity for auto_increment/datestamp
        if name == 'auto_increment' and value:
            object.__setattr__(self, 'datestamp', False)
        elif name == 'datestamp' and value:
            object.__setattr__(self, 'auto_increment', False)

        # Set the value
        object.__setattr__(self, name, value)

        # Auto-save (skip during loading)
        if not getattr(self, '_loading', True):
            self.save_config()

    def _log(self, level: str, message: str) -> None:
        """Log a message using the module logger.

        Args:
            level: Log level ('debug', 'info', 'warning', 'error')
            message: Message to log
        """
        getattr(logger, level)(message)

    @property
    def formatted_file_format(self) -> str:
        """File format with dot prefix (.png, .jpg)"""
        fmt = self.file_format
        return fmt if fmt.startswith('.') else f'.{fmt}'

    @property
    def default_save_directory(self) -> str:
        """Get the default save directory path"""
        return _default_save_directory()

    def _load_config(self) -> None:
        """Load configuration from file"""
        try:
            if self._config_file.exists():
                logger.debug(f"Loading config from: {self._config_file}")
                with open(self._config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Update fields with loaded values
                    for key, value in loaded_config.items():
                        if hasattr(self, key) and not key.startswith('_'):
                            object.__setattr__(self, key, value)
                logger.debug(f"Config loaded successfully, {len(loaded_config)} keys")
            else:
                logger.debug(f"No existing config file at: {self._config_file}")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")

    def save_config(self) -> None:
        """Save configuration to file"""
        try:
            # Ensure directory exists
            self._config_file.parent.mkdir(parents=True, exist_ok=True)

            # Filter out private fields for JSON serialization
            config_dict = {
                k: v for k, v in asdict(self).items()
                if not k.startswith('_')
            }

            # Always log the current application version
            config_dict['app_version'] = __version__

            with open(self._config_file, 'w') as f:
                json.dump(config_dict, f, indent=4)

            logger.debug(f"Config saved to: {self._config_file}")

        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")

    # Methods with side effects (kept as methods)

    def get_save_directory(self) -> str:
        """Get the save directory path, creating it if necessary"""
        dir_path = Path(self.save_directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        return str(dir_path)

    def get_default_save_directory(self) -> str:
        """Get the default save directory path"""
        return self.default_save_directory

    def set_save_directory(self, directory: str) -> None:
        """Set the save directory and update recent directories list"""
        # Add to recent directories if not already present
        if directory not in self.recent_directories:
            self.recent_directories.insert(0, str(directory))
            # Keep only the most recent 5 directories
            object.__setattr__(self, 'recent_directories', self.recent_directories[:5])

        self.save_directory = str(directory)

    def get_filename_with_suffix(self, filename: str = '') -> str:
        """Get filename with the configured file format suffix"""
        fmt = self.formatted_file_format
        if not filename.endswith(fmt):
            filename += fmt
        return filename
