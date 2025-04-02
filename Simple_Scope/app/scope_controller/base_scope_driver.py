"""
Controller for communicating with the oscilloscope via pyvisa
"""
import time
import pathlib
import pyvisa

class ScopeDriver:
    """Base Controller class for oscilloscope"""
    
    def __init__(self, address=None):
        self.resource_manager = None
        self.adaptor = None
        self._address = None
        
        self.address = address  # property to set the address


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


    def connect(self):
        """Connect to the oscilloscope"""
        if self.address is None:
            raise ValueError("Device address is not set.")
        
        self.resource_manager = pyvisa.ResourceManager()
        
        try:
            self.adaptor = self.resource_manager.open_resource(self.address)
            self.adaptor.timeout = 5000  # Set timeout to 5 seconds
            return True
        except Exception as e:
            print(f"Error connecting to device: {e}")
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
    
    
    def capture_screenshot(self, save_dir, filename, bg_color="white", save_waveform=False, metadata=None):
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
        
    
    def _save_waveform_data(self, file_path):
        """
        Save waveform data to a CSV file
        
        Args:
            file_path (Path or str): Path to save the waveform data
        """        
        raise NotImplementedError("This method should be implemented in a subclass.")
