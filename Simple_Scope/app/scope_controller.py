"""
Controller for communicating with the oscilloscope via pyvisa
"""

from pathlib import Path
import time
import pyvisa

class ScopeController:
    """Controller class for Tektronix MSO5x oscilloscope"""
    
    def __init__(self):
        self.resource_manager = pyvisa.ResourceManager()
        self.device = None
        self.device_id = None
    
    def scan_for_devices(self):
        """
        Scan for Tektronix MSO5x oscilloscopes
        
        Returns:
            str: Device ID if found, otherwise None
        """
        try:
            resources = self.resource_manager.list_resources()
            
            # Close any existing connection
            if self.device:
                self.device.close()
                self.device = None
                self.device_id = None
            
            # Look for Tektronix scope
            for resource in resources:
                try:
                    device = self.resource_manager.open_resource(resource)
                    idn = device.query("*IDN?").strip()
                    
                    # Check if it's a Tektronix MSO5x scope
                    if "TEKTRONIX" in idn and "MSO5" in idn:
                        self.device = device
                        self.device_id = idn
                        return idn
                    else:
                        # Not what we're looking for, close the resource
                        device.close()
                except Exception:
                    # Skip resources that cause errors
                    continue
            
            return None
        
        except Exception as e:
            print(f"Error scanning for devices: {str(e)}")
            raise
    
    def is_connected(self):
        """Check if a scope is connected"""
        return self.device is not None
    
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
        if not self.device:
            raise ValueError("No oscilloscope connected")
        
        # Create full path and ensure directory exists
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        file_path = save_path / filename
        
        try:
            # Set up the hardcopy parameters
            self.device.write(f"HARDCOPY:INKSAVER {0 if bg_color.lower() == 'black' else 1}")
            self.device.write("HARDCOPY:FORMAT PNG")
            self.device.write("HARDCOPY:LAYOUT PORTRAIT")
            
            # Capture the screenshot
            self.device.write("HARDCOPY START")
            
            # Wait a moment for the scope to generate the image
            time.sleep(1)
            
            # Get the screenshot data
            self.device.write("HARDCOPY:PORT USB")
            self.device.write(f"FILESYSTEM:WRITEFILE \"{str(file_path)}\"")
            
            # Save waveform data if requested
            if save_waveform:
                waveform_path = file_path.with_suffix('.csv')
                self._save_waveform_data(waveform_path)
            
            # Save metadata if provided
            if metadata:
                self._save_metadata(file_path, metadata)
            
            return str(file_path)
            
        except Exception as e:
            print(f"Error capturing screenshot: {str(e)}")
            raise
    
    def _save_waveform_data(self, file_path):
        """
        Save waveform data to a CSV file
        
        Args:
            file_path (Path or str): Path to save the waveform data
        """
        try:
            # Set up data export
            self.device.write("DATA:SOURCE CH1")
            self.device.write("DATA:ENCDG ASCII")
            self.device.write("DATA:START 1")
            self.device.write("DATA:STOP 10000")  # Adjust as needed
            
            # Get waveform data
            data = self.device.query("CURVE?")
            
            # Get scaling parameters
            x_inc = float(self.device.query("WFMOUTPRE:XINCR?"))
            y_mult = float(self.device.query("WFMOUTPRE:YMULT?"))
            y_off = float(self.device.query("WFMOUTPRE:YOFF?"))
            
            # Format data
            values = data.split(',')
            with open(file_path, 'w') as f:
                f.write("Time(s),Voltage(V)\n")
                for i, val in enumerate(values):
                    time_val = i * x_inc
                    voltage = float(val) * y_mult - y_off
                    f.write(f"{time_val:.9f},{voltage:.6f}\n")
                    
        except Exception as e:
            print(f"Error saving waveform data: {str(e)}")
    
    def _save_metadata(self, img_path, metadata):
        """
        Save metadata to a companion text file
        
        Args:
            img_path (Path or str): Path to the image file
            metadata (dict): Metadata to save
        """
        # Create metadata file path based on image path
        img_path = Path(img_path)
        metadata_path = img_path.with_stem(f"{img_path.stem}_metadata").with_suffix('.txt')
        
        with open(metadata_path, 'w') as f:
            f.write(f"Image file: {img_path.name}\n")
            f.write(f"Capture time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Device: {self.device_id}\n\n")
            
            # Write custom metadata
            f.write("Custom Metadata:\n")
            for key, value in metadata.items():
                f.write(f"{key}: {value}\n")
