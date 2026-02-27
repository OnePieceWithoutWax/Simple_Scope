"""
Controller for communicating with the oscilloscope via pyvisa
"""

# import time
# import pathlib
from pathlib import Path
from .base_scope_driver import ScopeDriver
from .base_scpi import SCPIMixin

class TektronixScopeDriver(ScopeDriver, SCPIMixin):
    """Controller class for Tektronix MSO5x oscilloscope"""

    _scope_temp_dir: str = "C:/temp"

    def __init__(self, address=None, name=None, logger=None):
        super().__init__(address=address, name=name, logger=logger)
        # Tektronix-specific init goes here

        self.setup_screenshot_dir()


    def setup_screenshot_dir(self) -> None:
        """Create temp directory and clear any existing files."""
        # Create directory on scope (will not error if it already exists)
        try:
            self.adaptor.write(f'FILESystem:MKDir "{self._scope_temp_dir}"')
            self._log('info', f"Scope temp directory ready: {self._scope_temp_dir}")
        except Exception as e:
            self._log('error', f"Note: {e} (directory may already exist)")
        # Clear all files in the temp directory
        self.clear_temp_directory()


    def clear_temp_directory(self) -> None:
        """
        Delete all files in the scope's temp directory.
        
        Args:
            scope: PyVISA instrument object
            self._scope_temp_dir: Path to temp directory on scope filesystem
        """
        try:
            # Get directory listing
            self.adaptor.write(f'FILESystem:CWD "{self._scope_temp_dir}"')
            dir_contents = self.adaptor.query('FILESystem:DIR?').strip()
            
            if dir_contents and dir_contents != '""':
                # Parse the directory listing (format may vary by scope model)
                # Typically returns comma-separated list of files
                files = [f.strip('"') for f in dir_contents.split(',') if f.strip()]
                
                for filename in files:
                    if filename and filename not in ['.', '..']:
                        file_path = f"{self._scope_temp_dir}/{filename}"
                        self.adaptor.write(f'FILESystem:DELEte "{file_path}"')
                        self._log('info', f"Deleted from scope: {file_path}")
            else:
                self._log('info', f"Scope temp directory is empty: {self._scope_temp_dir}")

        except Exception as e:
            self._log('error', f"Error clearing scope temp directory: {e}")


    def save_screenshot(self, save_dir, filename, suffix='.png', bg_color="white", save_waveform=False, metadata=None):
        """
        Capture a screenshot from the connected oscilloscope and save it
        
        Args:
            save_dir (str or Path): Directory to save the screenshot
            filename (str): Filename for the screenshot (with suffix)
            bg_color (str): Background color ("white" or "black")
            save_waveform (bool): Whether to save waveform data
            metadata (dict): Optional metadata to save
            
        Returns:
            str: Path to the saved file
        """
        if not self.adaptor:
            raise ValueError("No oscilloscope connected")
        
        # Create full path and ensure directory exists
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        filename = self.filename_with_suffix(filename, suffix)
        file_path = save_path / filename
        
        try:
            imgData = self.get_screenshot_brian()
            
            # Wait a moment for the scope to generate the image
            with open(file_path, "wb") as file:
                # file = open(fileName, "wb") # Save image data to local disk
                file.write(imgData)
                file.close()

            self._log("info", f"Saved: {file_path}")
            
            # Save waveform data if requested
            # if save_waveform:
            #     waveform_path = file_path.with_suffix('.csv')
            #     self._save_waveform_data(waveform_path)
            
            return str(file_path)
            
        except Exception as e:
            self._log("error", f"Error capturing screenshot: {str(e)}")
            raise

    def capture_screenshot(self, *args, **kwargs): #, save_dir=None, filename=None, suffix='.png', bg_color="white", save_waveform=False, metadata=None):
        ''' Returns an image of the scope screen, does not save it to disk. use save_screenshot() for that'''
        self._log("debug", "capture_screenshot called")
        return self.get_screenshot_brian()

    def get_screenshot_brian(self):
        ''' This method works when and AI cant figure it out
        does not work always...not sure why yet
        '''
        self._log("debug", "get_screenshot_brian: starting capture sequence")
        try:
            #Screen Capture on Tektronix Windows Scope
            self.adaptor.write(f'SAVE:IMAGe \"{self._scope_temp_dir}/temp.png\"') # Take a scope shot
            self._log("debug", f"wrote to save image at {self._scope_temp_dir}/temp.png on scope")
            self.adaptor.query('*OPC?') # Wait for instrument to finish writing image to disk
            self._log("debug", "OPC done")

            self.adaptor.write(f'FILESystem:READFile "{self._scope_temp_dir}/temp.png"') # Read temp image file from instrument

            img_data = self.adaptor.read_raw(1024*1024) # return that read...
            self._log("debug", "reading the image back to computer")

            self.adaptor.write(f'FILESystem:DELEte "{self._scope_temp_dir}/temp.png"') # Remove the Temp.png file
            self._log("debug", "Cleaning up temp file")
            self._log("debug", f"get_screenshot_brian: capture complete, {len(img_data)} bytes read")
            return img_data
        except Exception as e:
            code, message = self.next_error
            self._log("error", f"get_screenshot_brian: instrument error [{code}]: {message}")
            self._log("error", f"get_screenshot_brian: {e}")
            raise


    def _save_waveform_data(self, file_path):
        """
        Save waveform data to a CSV file
        
        Args:
            file_path (Path or str): Path to save the waveform data
        """
        try:
            # Set up data export
            self.adaptor.write("DATA:SOURCE CH1")
            self.adaptor.write("DATA:ENCDG ASCII")
            self.adaptor.write("DATA:START 1")
            self.adaptor.write("DATA:STOP 10000")  # Adjust as needed
            
            # Get waveform data
            data = self.adaptor.query("CURVE?")
            
            # Get scaling parameters
            x_inc = float(self.adaptor.query("WFMOUTPRE:XINCR?"))
            y_mult = float(self.adaptor.query("WFMOUTPRE:YMULT?"))
            y_off = float(self.adaptor.query("WFMOUTPRE:YOFF?"))
            
            # Format data
            values = data.split(',')
            with open(file_path, 'w') as f:
                f.write("Time(s),Voltage(V)\n")
                for i, val in enumerate(values):
                    time_val = i * x_inc
                    voltage = float(val) * y_mult - y_off
                    f.write(f"{time_val:.9f},{voltage:.6f}\n")
                    
        except Exception as e:
            self._log("error", f"Error saving waveform data: {str(e)}")

# The commented out `capture_screenshot_AI` method in the TektronixScopeDriver class is a method
# intended to capture a screenshot from the connected oscilloscope. It takes several parameters such
# as the directory to save the screenshot, the filename, background color, whether to save waveform
# data, and optional metadata.
        #needs work. but this is closer to how we want to save the data
    # def capture_screenshot_AI(self, save_dir, filename, bg_color="white", save_waveform=False, metadata=None):
    #     """
    #     Capture a screenshot from the connected oscilloscope
        
    #     Args:
    #         save_dir (str or Path): Directory to save the screenshot
    #         filename (str): Filename for the screenshot (with suffix)
    #         bg_color (str): Background color ("white" or "black")
    #         save_waveform (bool): Whether to save waveform data
    #         metadata (dict): Optional metadata to save
            
    #     Returns:
    #         str: Path to the saved file
    #     """
    #     if not self.adaptor:
    #         raise ValueError("No oscilloscope connected")
        
    #     # Create full path and ensure directory exists
    #     save_path = Path(save_dir)
    #     save_path.mkdir(parents=True, exist_ok=True)
    #     file_path = save_path / filename
        
    #     try:
    #         # Set up the hardcopy parameters
    #         self.adaptor.write(f"HARDCOPY:INKSAVER {0 if bg_color.lower() == 'black' else 1}")
    #         self.adaptor.write("HARDCOPY:FORMAT PNG")
    #         self.adaptor.write("HARDCOPY:LAYOUT PORTRAIT")
            
    #         # Capture the screenshot
    #         self.adaptor.write("HARDCOPY START")
            
    #         # Wait a moment for the scope to generate the image
    #         time.sleep(1)
            
    #         # Get the screenshot data
    #         self.adaptor.write("HARDCOPY:PORT USB")
    #         self.adaptor.write(f"FILESYSTEM:WRITEFILE \"{str(file_path)}\"")
            
    #         # Save waveform data if requested
    #         if save_waveform:
    #             waveform_path = file_path.with_suffix('.csv')
    #             self._save_waveform_data(waveform_path)
            
    #         return str(file_path)
            
    #     except Exception as e:
    #         print(f"Error capturing screenshot: {str(e)}")
    #         raise