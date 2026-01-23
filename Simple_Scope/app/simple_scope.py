import time
from pathlib import Path
from app.config import AppConfig
from .pyvisa_utils import find_instruments
from app.utils import get_next_incremented_filename, get_filename_with_datestamp, filename_with_suffix


class SimpleScope:
    """Main backend for the oscilloscope capture tool
    This class handles the connection to the oscilloscope and saving; everything non-GUI related.
    It also handles the configuration of the application
    and the metadata for the images captured.
    It can operate standalone (like in Jupyter), but is designed to be used with the GUI.
    """
    
    def __init__(self):
        self.scope = None
        self.scope_addr = None
        self.instrument_list = []
        self.meta = {}
        self.config = AppConfig()
        self.recent = dict(save_dir = None,
                            filename = None,
                            suffix = None,
                            save_path = None,
                            img_data = None,
                            metadata = None,
                            )
        self.selected_scope_driver = None
        self.device_id = None
    
    def scan_for_instruments(self, verbose=False):
        """Scan for connected instruments
        
        Args:
            verbose (bool): Whether to print detailed information
            
        Returns:
            list: List of dictionaries with instrument info
        """
        self.instrument_list = find_instruments(verbose)
        return self.instrument_list
        
    def auto_setup_scope(self):
        """Setup scope based on the instrument list"""
        for instr in self.instrument_list:
            manufacturer = instr.get("manufacturer", "")
            model_num = instr.get("model_num", "")
            
            # Check for supported scope models
            if manufacturer and model_num:
                if "TEKTRONIX" in manufacturer and "MSO5" in model_num:
                    from app.scope_controller import TektronixScopeDriver
                    self.device_id = instr
                    return self.setup_scope(instr["addr"], TektronixScopeDriver)
                elif "LECROY" in manufacturer.upper() and "WAVESURFER" in model_num.upper():
                    # Placeholder for Lecroy scope support
                    # from app.scope_controller import LecroyScopeDriver
                    # return self.setup_scope(instr["addr"], LecroyScopeDriver)
                    return False
        
        return False  # No compatible scope found


    def setup_scope(self, address, driver=None):
        """Setup connection to a scope
        
        Args:
            address (str): VISA address string
            driver (class, optional): Scope driver class
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if driver is not None:
            self.selected_scope_driver = driver
            
        if self.selected_scope_driver is None:
            return False
            
        try:
            self.scope_addr = address
            self.scope = self.selected_scope_driver(self.scope_addr)
            # alternativly: self.scope.address = self.scope_addr
            result = self.scope.connect()
            
            if result:
                # Save the device ID for metadata
                self.device_id = f"{self.scope_addr}"
                for instr in self.instrument_list:
                    if instr.get("addr") == self.scope_addr:
                        model = instr.get("model_num", "")
                        serial = instr.get("serial_num", "")
                        if model and serial:
                            self.device_id = f"{model} (SN: {serial})"
                        break
            
            return result
        except Exception as e:
            print(f"Error setting up scope: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from the scope"""
        if self.scope:
            self.scope.disconnect()
            self.scope = None
            self.scope_addr = None
            return True
        return False

    def is_connected(self):
        """Check if scope is connected
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.scope is not None and self.scope.is_connected()
    
    def get_device_info(self):
        """Get connected device information
        
        Returns:
            str: Device information or None if not connected
        """
        if self.is_connected():
            return self.device_id
        return None

    def capture(self, save_dir=None, filename=None, suffix=None, bg_color="white", save_waveform=False, metadata=None):
        """
        Capture a screenshot from the connected oscilloscope
        
        Args:
            save_dir (str or Path, optional): Directory to save the screenshot. Defaults to config.
            filename (str, optional): Filename for the screenshot. Defaults to config.
            bg_color (str): Background color ("white" or "black")
            save_waveform (bool): Whether to save waveform data
            metadata (dict): Optional metadata to save
            
        Returns:
            str: Path to the saved file
        """
        if not self.scope:
            raise ValueError("No oscilloscope connected")
        
        # Use config values if not specified
        if save_dir is None:
            save_dir = self.config.get_save_directory()
            
        if filename is None:
            filename = self.config.default_filename

        if suffix is None:
            suffix = self.config.formatted_file_format

        # Ensure directory exists
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Capture screenshot
        screenshot_data = self.scope.capture_screenshot(bg_color, save_waveform)
        self.save_file(save_dir, filename, suffix, screenshot_data)  # Save the image data to disk
        # Save metadata if provided
        if metadata:
            self.meta = metadata
            self._save_metadata(save_dir, filename)
            
            # Update config with the metadata
            self.config.last_used_metadata = metadata
        
        # Update the config with the new directory
        self.config.set_save_directory(save_dir)
        
        # Update the recent dict with the new directory
        self.recent = dict(save_dir = save_dir,
                            filename = filename,
                            suffix = suffix,
                            save_path = save_path,
                            screenshot_data = screenshot_data,
                            wave_data = None,
                            metadata = metadata,
                            )
        return screenshot_data

    def _save_metadata(self, save_dir, filename):
        """
        Save metadata to a companion text file
        
        Args:
            save_dir (Path or str): Directory where the image is saved
            filename (str): Filename of the image
        """
        # Create metadata file path based on image path
        path = Path(save_dir) / filename
        metadata_path = path.with_stem(f"{path.stem}_metadata").with_suffix('.txt')
        
        with open(metadata_path, 'w') as f:
            f.write(f"Image file: {path.name}\n")
            f.write(f"Capture time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            if self.device_id:
                f.write(f"Device: {self.device_id}\n\n")
            
            # Write custom metadata
            f.write("Custom Metadata:\n")
            for key, value in self.meta.items():
                f.write(f"{key}: {value}\n")
        
        
    def save_file(self, save_dir, filename, suffix, file_data):
        filename = filename_with_suffix(filename, suffix)
        file_path = Path(save_dir) / filename

        with open(file_path, "wb") as file:
            # file = open(fileName, "wb") # Save image data to local disk
            file.write(file_data)
            file.close()

        print(f"Saved: {file_path}") #logging?

        return file_path

    def get_capture_filename(self, save_dir=None, base_filename=None, suffix=None):
        """
        Generate the appropriate filename based on config settings (auto_increment, datestamp).

        Args:
            save_dir (str or Path, optional): Directory for the file. Defaults to config.
            base_filename (str, optional): Base filename. Defaults to config.
            suffix (str, optional): File extension. Defaults to config.

        Returns:
            str: The generated filename (with extension, without path)
        """
        if save_dir is None:
            save_dir = self.config.get_save_directory()
        if base_filename is None:
            base_filename = self.config.default_filename
        if suffix is None:
            suffix = self.config.formatted_file_format

        if self.config.auto_increment:
            return get_next_incremented_filename(save_dir, base_filename, suffix)
        elif self.config.datestamp:
            return get_filename_with_datestamp(save_dir, base_filename, suffix)
        else:
            return filename_with_suffix(base_filename, suffix)