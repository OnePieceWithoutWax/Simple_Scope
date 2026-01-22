"""
Utility functions for the Oscilloscope Screenshot Capture Application
"""

from pathlib import Path
import re
import platform
import subprocess
import os  # Kept for environment variables
import datetime

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


def get_new_filepath(filename, directory, suffix=""):
    """
    Generate a new filename by incrementing the counter if needed.
    
    Args:
        base_filename (str): The base filename
    """


    
    filepath = Path(directory) / filename_with_suffix(filename, suffix)
    if not filepath.exists():
        return filepath
    
    # Extract filenames and sort them
    existing_filenames = [f.name for f in existing_files]
    existing_filenames.sort()
    
    # Start with the base filename and increment until a unique one is found
    new_filename = base_filename
    while new_filename in existing_filenames:
        new_filename = increment_filename(new_filename)
    
    return new_filename


def increment_filename(filename):
    """
    Increment the counter in the filename.
    Looks for pattern like "_001" at the end of the filename (before extension).
    
    Args:
        filename (str): Current filename
        
    Returns:
        str: Filename with incremented counter
    """
    file_path = Path(filename)
    base = file_path.stem
    ext = file_path.suffix
    
    # Look for underscore followed by digits at the end of the stem
    # Pattern: ends with underscore followed by one or more digits
    match = re.search(r'_(\d+)$', base)
    
    if match:
        # Extract the counter value and its position
        counter_str = match.group(1)
        counter_val = int(counter_str)
        num_digits = len(counter_str)
        
        # Increment and pad with zeros to maintain the same length
        new_counter = str(counter_val + 1).zfill(num_digits)
        
        # Replace the old counter with the new one
        new_base = base[:match.start()] + '_' + new_counter
        return new_base + ext
    else:
        # If no _### pattern found at end, append _001
        return base + "_001" + ext
    
    

def filename_with_datestamp(base_filename):
    """
    Generate filename with datestamp appended

    Args:
        base_filename (str): The base filename

    Returns:
        str: Filename with datestamp appended
    """
    # Get current timestamp
    timestamp = datetime.datetime.now().strftime("%Y.%m.%d_%H.%M.%S")

    # Split filename and extension
    path = Path(base_filename)
    stem = path.stem
    suffix = path.suffix

    # Append timestamp before the extension
    return f"{stem}_{timestamp}{suffix}"