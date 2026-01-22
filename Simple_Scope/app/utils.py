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


def get_next_incremented_filename(directory, base_filename, suffix):
    """
    Find the next available filename by appending _001, _002, etc.
    Checks if file exists and increments until a free slot is found.

    Args:
        directory (str or Path): Directory to check for existing files
        base_filename (str): Base filename without incrementor
        suffix (str): File extension (e.g., "png" or ".png")

    Returns:
        str: Filename with incrementor appended (e.g., "capture_001.png")
    """
    directory = Path(directory)
    stem = Path(base_filename).stem
    ext = suffix if suffix.startswith('.') else '.' + suffix

    counter = 1
    while True:
        # Use zfill(3) for 001-999, allow natural growth beyond
        if counter < 1000:
            incrementor = str(counter).zfill(3)
        else:
            incrementor = str(counter)

        new_filename = f"{stem}_{incrementor}{ext}"
        filepath = directory / new_filename

        if not filepath.exists():
            return new_filename

        counter += 1


def get_filename_with_datestamp(directory, base_filename, suffix):
    """
    Generate filename with datestamp appended, handling collisions.
    If the timestamped filename already exists, waits 100ms and retries
    (the timestamp will naturally change as time passes).

    Args:
        directory (str or Path): Directory to check for existing files
        base_filename (str): Base filename without datestamp
        suffix (str): File extension (e.g., "png" or ".png")

    Returns:
        str: Filename with datestamp appended (e.g., "capture_2026.01.22_10.30.45.png")
    """
    import time

    directory = Path(directory)
    stem = Path(base_filename).stem
    ext = suffix if suffix.startswith('.') else '.' + suffix

    for _ in range(100):  # Try up to 100 times (~10 seconds max)
        timestamp = datetime.datetime.now().strftime("%Y.%m.%d_%H.%M.%S")
        new_filename = f"{stem}_{timestamp}{ext}"
        filepath = directory / new_filename

        if not filepath.exists():
            return new_filename

        # Wait 100ms for timestamp to change
        time.sleep(0.1)

    raise ValueError("Could not generate unique filename after 100 attempts")