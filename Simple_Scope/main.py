#!/usr/bin/env python3
"""
Oscilloscope Screenshot Capture Application
Entry point for the application
"""

import sys
import os
from pathlib import Path
from app.gui import ScopeCaptureGUI

def main():
    """Main entry point for the application"""
    app = ScopeCaptureGUI()
    app.mainloop()

if __name__ == "__main__":
    # This helps PyInstaller find the correct path
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle
        application_path = Path(sys._MEIPASS)
    else:
        # If the application is run from script
        application_path = Path(__file__).parent
    
    # Change to application directory
    # Path.cwd().chdir(application_path)
    os.chdir(application_path)
    main()
