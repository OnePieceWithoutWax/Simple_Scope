"""
Utility functions for the Oscilloscope Screenshot Capture Application
"""

from pathlib import Path
import re
import platform
import subprocess
import os  # Kept for environment variables

def expand_environment_vars(path):
    """
    Expand environment variables in the path
    
    Args:
        path (str or Path): Path with potential environment variables
        
    Returns:
        Path: Path object with expanded environment variables
    """
    path_str = str(path)
    
    # Handle %USERNAME% style variables for Windows
    if platform.system() == "Windows":
        username_match = re.search(r'%USERNAME%', path_str)
        if username_match:
            username = os.environ.get('USERNAME', '')
            path_str = path_str.replace('%USERNAME%', username)
    
    # Handle standard environment variables and convert to Path
    expanded_path = Path(os.path.expandvars(path_str)).expanduser()
    return expanded_path

def open_file_explorer(path):
    """
    Open the file explorer at the specified path
    
    Args:
        path (str or Path): Path to open in file explorer
    """
    path_obj = Path(path)
    if not path_obj.exists():
        path_obj.mkdir(parents=True, exist_ok=True)
        
    if platform.system() == "Windows":
        os.startfile(str(path_obj))
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", str(path_obj)])
    else:  # Linux and other
        subprocess.run(["xdg-open", str(path_obj)])

def get_system_info():
    """
    Get system information
    
    Returns:
        dict: Dictionary with system information
    """
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
    }

def parse_visa_resource_string(resource_string):
    """
    Parse VISA resource string to extract information
    
    Args:
        resource_string (str): VISA resource string
        
    Returns:
        dict: Dictionary with parsed information
    """
    info = {
        "original": resource_string,
        "type": "unknown",
    }
    
    # Handle USB devices
    usb_match = re.match(
        r'USB[0-9]*::([0-9]*)::([0-9]*)::([^::]*)(?:::INSTR)?', 
        resource_string
    )
    if usb_match:
        info["type"] = "usb"
        info["vendor_id"] = usb_match.group(1)
        info["product_id"] = usb_match.group(2)
        info["serial_number"] = usb_match.group(3)
    
    # Handle TCPIP devices
    tcpip_match = re.match(
        r'TCPIP[0-9]*::([^::]*)::[0-9]*::SOCKET', 
        resource_string
    )
    if tcpip_match:
        info["type"] = "tcpip"
        info["address"] = tcpip_match.group(1)
    
    return info
