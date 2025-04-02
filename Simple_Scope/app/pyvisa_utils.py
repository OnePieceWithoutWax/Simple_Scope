"""
Utility functions for the Oscilloscope Screenshot Capture Application
"""
import pyvisa


        # self.resource_manager = pyvisa.ResourceManager()
        # self.device = None
        # self.device_id = None

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