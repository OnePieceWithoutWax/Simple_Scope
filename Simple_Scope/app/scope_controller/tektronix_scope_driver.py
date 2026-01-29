"""
Controller for communicating with the oscilloscope via pyvisa
"""

# import time
# import pathlib
from pathlib import Path
from .base_scope_driver import ScopeDriver

class TektronixScopeDriver(ScopeDriver):
    """Controller class for Tektronix MSO5x oscilloscope"""
    


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
        return self.get_screenshot_brian()

    def get_screenshot_brian(self):
        ''' This method works when and AI cant figure it out'''
        #Screen Capture on Tektronix Windows Scope
        self.adaptor.write('SAVE:IMAGe \"C:/Temp.png\"') # Take a scope shot
        self.adaptor.query('*OPC?') # Wait for instrument to finish writing image to disk
        
        self.adaptor.write('FILESystem:READFile "C:/Temp.png"') # Read temp image file from instrument
        
        img_data = self.adaptor.read_raw(1024*1024) # return that read...
        
        self.adaptor.write('FILESystem:DELEte "C:/Temp.png"') # Remove the Temp.png file
        
        return img_data


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