"""
Utility functions for the Oscilloscope Screenshot Capture Application
Source from: nwlab.lab.pymeasure_extensions
"""
import pyvisa
from typing import Dict, List, Optional, Any


def scpi_id_parser(id_string: str) -> Dict[str, Optional[str]]:
    """
    Parse the SCPI identification string into its components.
    
    Parameters:
    -----------
    id_string : str
        The identification string returned by *IDN? command
        
    Returns:
    --------
    Dict[str, Optional[str]]
        Dictionary containing manufacturer, model_num, serial_num, and software_rev
    """
    # Initialize with None values
    result = {
        "manufacturer": None,
        "model_num": None,
        "serial_num": None,
        "software_rev": None
    }
    
    # Only try to parse if we have a non-empty string
    if id_string and isinstance(id_string, str):
        id_parts = id_string.split(',')
        if len(id_parts) >= 4:
            result["manufacturer"] = id_parts[0].strip()
            result["model_num"] = id_parts[1].strip()
            result["serial_num"] = id_parts[2].strip()
            result["software_rev"] = id_parts[3].strip()
    
    return result


def find_instruments(verbose: bool = False) -> List[Dict[str, Any]]:
    """
    Find and identify all VISA instruments connected to the system.
    
    This function searches for all VISA resources, attempts to communicate with each
    instrument, and retrieves its identification information.
    
    Parameters:
    -----------
    verbose : bool, optional
        Whether to print detailed information during discovery (default: False)
        
    Returns:
    --------
    List[Dict[str, Any]]
        List of dictionaries, each containing information about a found instrument:
        - n: index number
        - addr: VISA address
        - id: raw identification string
        - manufacturer: parsed manufacturer name
        - model_num: parsed model number
        - serial_num: parsed serial number
        - software_rev: parsed software revision
    """
    rm = pyvisa.ResourceManager()
    found = []
    
    try:
        instrs = rm.list_resources()
        
        for n, instr in enumerate(instrs):
            instrument_info = {
                "n": n,
                "addr": instr,
                "id": "Not known",
                "manufacturer": None,
                "model_num": None,
                "serial_num": None,
                "software_rev": None
            }
            
            # Try to communicate with the instrument
            try:
                res = rm.open_resource(instr)
                try:
                    # Query instrument identification
                    idn = res.query('*idn?').strip()
                    instrument_info["id"] = idn
                    # Parse the identification string
                    instrument_info.update(scpi_id_parser(idn))
                except pyvisa.Error as query_error:
                    if verbose:
                        print(f"Cannot query identification for {instr}: {query_error}")
                finally:
                    # Always close the resource
                    res.close()
            except pyvisa.VisaIOError as e:
                if verbose:
                    print(f"{n}: {instr}: Visa IO Error: check connections")
                    print(f"Error details: {e}")
            
            if verbose:
                print(f"{n}: {instr}: {instrument_info['id']}")
            
            found.append(instrument_info)
    
    finally:
        # Ensure the resource manager is closed
        rm.close()
    
    return found
