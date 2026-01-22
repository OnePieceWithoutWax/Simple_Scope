"""
Configuration management for the application
"""

import json
import re
from pathlib import Path

class AppConfig:
    """Configuration manager for the application"""
    
    def __init__(self, config_file=None):
        """
        Initialize configuration manager
        
        Args:
            config_file (Path or str, optional): Path to config file. If None, uses default location.
        """
        # Default locations
        self.app_data_dir = Path.home() / ".scope_capture"
        
        if config_file is None:
            self.config_file = self.app_data_dir / "config.json"
        else:
            self.config_file = Path(config_file)
        
        # Default configuration
        self.config = {
            "save_directory": str(Path.home() / "Pictures" / "scope_capture"),
            "default_filename": "capture", # No suffix required
            "filename": None,
            "file_format": "png",
            "background_color": "white",
            "save_waveform": False,
            "auto_increment": False,
            "datestamp": False,
            "last_used_metadata": {},
            "recent_directories": [],
        }
        
        # Load existing configuration if it exists
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Update existing config with loaded values
                    self.config.update(loaded_config)
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
    
    def save_config(self):
        """Save configuration to file"""
        # pass
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
                
        except Exception as e:
            print(f"Error saving configuration: {str(e)}") #really need to add logging herel
    
    
    def get_save_directory(self):
        """Get the save directory path"""
        # Ensure directory exists
        dir_path = Path(self.config["save_directory"])
        dir_path.mkdir(parents=True, exist_ok=True)
        return str(dir_path)
    
    def set_save_directory(self, directory):
        """Set the save directory path"""
        self.config["save_directory"] = str(directory)
        
        # Add to recent directories if not already present
        if directory not in self.config["recent_directories"]:
            self.config["recent_directories"].insert(0, str(directory))
            # Keep only the most recent 5 directories
            self.config["recent_directories"] = self.config["recent_directories"][:5]
        
        self.save_config()
    
    def get_default_file_format(self):
        """Get the default filename"""
        if '.' not in self.config["file_format"]:
            self.config["file_format"] = '.' + self.config["file_format"]
        return self.config["file_format"]
    
    def set_default_file_format(self, file_format):
        """Get the default filename"""
        self.config["file_format"] = file_format

    def get_default_filename(self):
        """Get the default filename"""
        return self.config["default_filename"]

    def get_filename(self):
        """Get the filename"""
        if self.config["filename"] is None:
            return self.get_default_filename()
        return self.config["filename"]

    def set_filename(self, filename):
        """Get the filename"""
        self.config["filename"] = filename
        self.save_config()

    def set_default_filename(self, filename):
        """Set the default filename"""
        self.config["default_filename"] = filename
        self.save_config()
    
    def get_metadata_fields(self):
        """Get the last used metadata fields"""
        return self.config["last_used_metadata"]
    
    def set_metadata_fields(self, metadata):
        """Set the metadata fields"""
        self.config["last_used_metadata"] = metadata
        self.save_config()

    def get_auto_increment(self):
        """Get the auto increment setting"""
        return self.config.get("auto_increment", False)

    def set_auto_increment(self, enabled):
        """Set the auto increment setting"""
        self.config["auto_increment"] = enabled
        # Auto increment and datestamp are mutually exclusive
        if enabled:
            self.config["datestamp"] = False
        self.save_config()

    def get_datestamp(self):
        """Get the datestamp setting"""
        return self.config.get("datestamp", False)

    def set_datestamp(self, enabled):
        """Set the datestamp setting"""
        self.config["datestamp"] = enabled
        # Auto increment and datestamp are mutually exclusive
        if enabled:
            self.config["auto_increment"] = False
        self.save_config()
    
    def update_config(self, key, value):
        """Update a configuration value"""
        if key in self.config:
            self.config[key] = value
            self.save_config()
            return True
        return False
    
    def get_filename_with_suffix(self, filename=''):
        """Get the default filename"""
        if '.' not in self.config["file_format"]:
            self.config["file_format"] = '.' + self.config["file_format"]
        if not filename.endswith(self.config["file_format"]):
            filename += self.config["file_format"]
        return filename
    
    def get_next_filename(self, base_dir=None):
        """
        Get the next available filename in sequence
        
        Args:
            base_dir (Path or str, optional): Directory to check. If None, uses save_directory.
        
        Returns:
            str: Next available filename
        """
        if base_dir is None:
            base_dir = Path(self.get_save_directory())
        else:
            base_dir = Path(base_dir)
        
        filename = self.get_default_filename()
        stem = Path(filename).stem
        suffix = Path(filename).suffix
        
        # Look for numeric suffix
        match = re.search(r'(\d+)', stem)
        
        if match:
            # Extract base name and number
            base_name = stem[:match.start()]
            num_str = match.group(1)
            num_digits = len(num_str)
            counter = int(num_str)
            
            # Find the next available filename
            while True:
                counter += 1
                new_name = f"{base_name}{counter:0{num_digits}d}{suffix}"
                if not (base_dir / new_name).exists():
                    return new_name
        else:
            # No numeric suffix, add _001
            counter = 1
            while True:
                new_name = f"{stem}_{counter:03d}{suffix}"
                if not (base_dir / new_name).exists():
                    return new_name
                counter += 1
