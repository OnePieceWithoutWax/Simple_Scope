import time
import pathlib
from pathlib import Path
from app.config import AppConfig
from .pyvisa_utils import find_instruments


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
            filename = self.config.get_default_filename()

        if suffix is None:
            suffix = self.config.get_default_suffix()

        # Ensure directory exists
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Capture screenshot
        file_path = self.scope.capture_screenshot(
            save_dir, filename, suffix, bg_color, save_waveform, metadata
        )
            
        # Save metadata if provided
        if metadata:
            self.meta = metadata
            self._save_metadata(save_dir, filename)
            
            # Update config with the metadata
            self.config.set_metadata_fields(metadata)
        
        # Update the config with the new directory
        self.config.set_save_directory(save_dir)
        
        return file_path

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


    # TODO we should be keeping track of the filename here, as its is backend responsibility
            # next_filename = self._increment_filename(filename)
            # self.filename_var.set(next_filename)
    # def _increment_filename(self, filename):
    #     """Increment the counter in the filename"""
    #     # Find the last sequence of digits in the filename
    #     file_path = Path(filename)
    #     base = file_path.stem
    #     ext = file_path.suffix
    #     match = re.search(r'(\d+)(?!.*\d)', base)
        
    #     if match:
    #         # Extract the counter value and its position
    #         counter_str = match.group(1)
    #         counter_val = int(counter_str)
            
    #         # Increment and pad with zeros to maintain the same length
    #         new_counter = str(counter_val + 1).zfill(len(counter_str))
            
    #         # Replace the old counter with the new one
    #         new_base = base[:match.start(1)] + new_counter + base[match.end(1):]
    #         return new_base + ext
    #     else:
    #         # If no counter found, just append _001
    #         return base + "_001" + ext