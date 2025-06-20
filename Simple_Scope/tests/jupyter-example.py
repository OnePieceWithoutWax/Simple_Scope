# Example of using SimpleScope in a Jupyter notebook

from Simple_Scope.app.simple_scope import SimpleScope
import pandas as pd
from IPython.display import Image, display

# Initialize SimpleScope
scope = SimpleScope()

# Scan for instruments
instruments = scope.scan_for_instruments(verbose=True)

# Display available instruments as a DataFrame
instruments_df = pd.DataFrame(instruments)
display(instruments_df)

# Try to auto-connect to a compatible scope
connected = scope.auto_setup_scope()
print(f"Connected: {connected}")

if connected:
    # Get device info
    print(f"Device: {scope.get_device_info()}")
    
    # Capture a screenshot
    # You can customize the directory, filename, background color, etc.
    file_path = scope.capture(
        save_dir="./captures",
        filename="jupyter_capture_001.png",
        bg_color="white",
        save_waveform=True,
        metadata={"Project": "Jupyter Demo", "Engineer": "Your Name"}
    )
    
    # Display the captured image
    display(Image(file_path))
    
    # Disconnect when done
    scope.disconnect()
