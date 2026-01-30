"""
Controller for communicating with the oscilloscope via pyvisa
"""
# import time
# import pathlib
import pyvisa

class ScopeDriver:
    """Base Controller class for oscilloscope
    methods intended to be overridden in subclasses should have:
    args and kwargs, and NotImplementedError
    b/c we had issue with args mismatch that was "hard" to debug
    since we didnt see the NotImplementedError, we were debugging the wrong thing
    """
    
    def __init__(self, address=None, name=None, logger=None):
        self.resource_manager = None
        self.adaptor = None
        self.name = name
        self._address = None
        self.logger = logger

        self.address = address  # property to set the address

    def _log(self, level: str, message: str) -> None:
        """Log a message if logger is available.

        Args:
            level: Log level ('debug', 'info', 'warning', 'error')
            message: Message to log
        """
        if self.logger:
            getattr(self.logger, level)(message)


    @property
    def address(self):
        """Get the device address"""
        return self._address

    @address.setter
    def address(self, address):
        """Set the device address"""
        if self.adaptor is not None:
            self.adaptor.close()
        self._address = address
        self.adaptor = None  # Reset device to None when address changes
        if address is not None:
            self.connect()  # Attempt to connect to the new address

    def connect(self, address=None):
        """Connect to the oscilloscope"""
        if address is not None:
            self.address = address

        if self.address is None: # assert self.address is not None,
            raise ValueError("Device address is not set.")
        
        self.resource_manager = pyvisa.ResourceManager()
        
        try:
            self.adaptor = self.resource_manager.open_resource(self.address)
            self.adaptor.timeout = 5000  # Set timeout to 5 seconds
            self._log("info", f"Connected to device at {self.address}")
            return True
        except Exception as e:
            self._log("error", f"Error connecting to device: {e}")
            return False
        

    def disconnect(self):
        """Disconnect from the oscilloscope"""
        if self.adaptor is not None:
            self.adaptor.close()
            self.adaptor = None
            # print("Disconnected from oscilloscope.") # replace with logging maybe
        else:
            # print("No oscilloscope connected.")
            pass
        
        if self.resource_manager is not None:
            # self.resource_manager.close() # or equivialent?
            self.resource_manager = None


    def is_connected(self):
        """Check if a scope is connected"""
        return self.adaptor is not None
    
    
    @staticmethod
    def filename_with_suffix(filename: str, suffix: str) -> str: 
        """
        Append suffix to filename before the extension
        
        Args:
            filename (str): Original filename
            suffix (str): Suffix to append
            
        Returns:
            str: Filename with appended suffix
        """
        if not suffix.startswith("."):
            suffix = "." + suffix
        
        if filename.endswith(suffix):
            return filename
        
        filename = filename + suffix
        return filename   


    def capture_screenshot(self, save_dir, filename, suffix='.png',  bg_color="white", save_waveform=False, metadata=None, *args, **kwargs):
        """
        Capture a screenshot from the connected oscilloscope
        
        Args:
            save_dir (str or Path): Directory to save the screenshot
            filename (str): Filename for the screenshot
            bg_color (str): Background color ("white" or "black")
            save_waveform (bool): Whether to save waveform data
            metadata (dict): Optional metadata to save
            
        Returns:
            str: Path to the saved file
        """

        raise NotImplementedError("This method should be implemented in a subclass.")
        
    
    def _save_waveform_data(self, file_path, *args, **kwargs):
        """
        Save waveform data to a CSV file
        
        Args:
            file_path (Path or str): Path to save the waveform data
        """        
        raise NotImplementedError("This method should be implemented in a subclass.")

