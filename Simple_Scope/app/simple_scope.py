# from app.scope_controller import TektronixScopeDriver as ScopeController
import time
import pathlib
from app.config import AppConfig
from .pyvisa_utils import find_instruments


class SimpleScope():
    """Main backend for the oscilloscope capture tool
    this class handles the connection to the oscilloscope, and saveing, everything non gui related
    it also handles the configuration of the application
    and the metadata for the images captured.
    it can operate standalone (like in jupyter), but is designed to be used with the GUI.
    """
    
    def __init__(self):
        self.scope = None
        self.scope_addr = None
        self.instrument_list = []
        self.meta = {}
        self.config = AppConfig()
        self.selected_scope_driver = None
        
        # Auto-scan for scope on startup
        self.after(500, self.scan_for_scope) #?
    
    def scan_for_instruments(self):
        self.instrument_list = find_instruments()
        return self.instrument_list
        
    def auto_setup_scope(self):
        """setup scope based on the instrument list"""
        for instr in self.instrument_list:
            if "TEKTRONIX" in instr["manufacturer"] and "MSO5" in instr["model_num"]: # should this be a witch staement?
                from app.scope_controller import TektronixScopeDriver
                self.setup_scope(instr["addr"], TektronixScopeDriver)
                break
            elif "Lecroy" in instr["manufacturer"] and "Wavesurfer" in instr["model_num"]:
                # from app.scope_controller import LecroyScopeDriver
                # self.setup_scope(instr["addr"], LecroyScopeDriver)
                # break
                pass # placeholder for Lecroy scope, and other scopes...


    def setup_scope(self, address, driver=None):
        if driver is not None:
            self.selected_scope_driver = driver
        assert self.selected_scope_driver is not None, "No scope driver selected"
        self.scope = self.selected_scope_driver()
        self.scope.connect(address)


    def capture(self, save_dir, filename, save_waveform=False, metadata=False):
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
        if not self.scope:
            raise ValueError("No oscilloscope connected")
        
        self.scope.capture_screenshot(save_dir, filename, save_waveform=save_waveform)
            
        # Save metadata if provided
        if metadata:
            self._save_metadata(save_dir, filename)


    def _save_metadata(self, save_dir, filename):
        """
        Save metadata to a companion text file
        
        Args:
            img_path (Path or str): Path to the image file
            metadata (dict): Metadata to save
        """
        # Create metadata file path based on image path
        path = pathlib.Path(save_dir) / filename
        metadata_path = path.with_stem(f"{path.stem}_metadata").with_suffix('.txt')
        
        with open(metadata_path, 'w') as f:
            f.write(f"Image file: {path.name}\n")
            f.write(f"Capture time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Device: {self.device_id}\n\n")
            
            # Write custom metadata
            f.write("Custom Metadata:\n")
            for key, value in self.meta.items():
                f.write(f"{key}: {value}\n")