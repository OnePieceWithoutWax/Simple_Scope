"""
GUI implementation for the Oscilloscope Screenshot Capture Application
"""

from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
from app.simple_scope import SimpleScope

class ScopeCaptureGUI(tk.Tk):
    """Main application window for the oscilloscope capture tool"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Scope Capture")
        self.geometry("600x400")
        
        # Initialize backend
        self.scope = SimpleScope()
        
        # Create and configure the notebook (tabbed interface)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.setup_tab = ttk.Frame(self.notebook)
        self.main_tab = ttk.Frame(self.notebook)
        self.metadata_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.setup_tab, text="Setup")
        self.notebook.add(self.main_tab, text="Scope")
        self.notebook.add(self.metadata_tab, text="Metadata")
        
        # Initialize the tabs
        self._initialize_setup_tab()
        self._initialize_main_tab()
        self._initialize_metadata_tab()
        
        # Auto-scan for scope on startup
        self.after(500, self.scan_for_scope)
    
    def _initialize_setup_tab(self):
        """Initialize the Setup tab with its UI elements"""
        frame = ttk.Frame(self.setup_tab, padding=(20, 10))
        frame.pack(fill='both', expand=True)
        
        # Connection status
        self.connection_status = ttk.Label(frame, text="Status: Not Connected")
        self.connection_status.pack(anchor='w', pady=(0, 20))
        
        # Scan button
        scan_button = ttk.Button(frame, text="Scan for Scope", command=self.scan_for_scope)
        scan_button.pack(anchor='w')
        
        # Device info
        self.device_info = ttk.Label(frame, text="No device detected")
        self.device_info.pack(anchor='w', pady=(20, 0))
    
    def _initialize_main_tab(self):
        """Initialize the Main tab with its UI elements"""
        frame = ttk.Frame(self.main_tab, padding=(20, 10))
        frame.pack(fill='both', expand=True)
        
        # Save Directory
        ttk.Label(frame, text="Save Directory:").grid(row=0, column=0, sticky='w', pady=5)
        
        self.save_dir_var = tk.StringVar(value=self.scope.config.get_save_directory())
        save_dir_entry = ttk.Entry(frame, textvariable=self.save_dir_var, width=40)
        save_dir_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(5, 0))
        
        browse_button = ttk.Button(frame, text="Browse", command=self.browse_directory)
        browse_button.grid(row=0, column=2, sticky='w', pady=5, padx=(5, 0))
        
        # Filename
        ttk.Label(frame, text="Filename:").grid(row=1, column=0, sticky='w', pady=5)
        
        self.filename_var = tk.StringVar(value=self.scope.config.get_default_filename())
        filename_entry = ttk.Entry(frame, textvariable=self.filename_var, width=40)
        filename_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=(5, 0))
        
        # File format
        ttk.Label(frame, text="File Format:").grid(row=2, column=0, sticky='w', pady=5)
        
        self.file_format_var = tk.StringVar(value="png")
        file_format_combo = ttk.Combobox(frame, textvariable=self.file_format_var, 
                                         values=["png"], state="readonly", width=10)
        file_format_combo.grid(row=2, column=1, sticky='w', pady=5, padx=(5, 0))
        
        # Background color
        ttk.Label(frame, text="Background:").grid(row=3, column=0, sticky='w', pady=5)
        
        self.bg_color_var = tk.StringVar(value="white")
        bg_color_combo = ttk.Combobox(frame, textvariable=self.bg_color_var, 
                                     values=["white", "black"], state="readonly", width=10)
        bg_color_combo.grid(row=3, column=1, sticky='w', pady=5, padx=(5, 0))
        
        # Save waveform data
        self.save_waveform_var = tk.BooleanVar(value=False)
        save_waveform_check = ttk.Checkbutton(frame, text="Save waveform data", 
                                             variable=self.save_waveform_var)
        save_waveform_check.grid(row=4, column=0, columnspan=2, sticky='w', pady=10)
        
        # Capture button
        capture_button = ttk.Button(frame, text="Capture", command=self.capture_screenshot)
        capture_button.grid(row=5, column=0, columnspan=2, sticky='w', pady=10)
        
    def _initialize_metadata_tab(self):
        """Initialize the Metadata tab with dynamic UI elements"""
        frame = ttk.Frame(self.metadata_tab, padding=(20, 10))
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Metadata fields will appear here when configured").pack(pady=20)
        
        # This will be populated dynamically based on the metadata dict
        self.metadata_fields = {}
        self.metadata_frame = ttk.Frame(frame)
        self.metadata_frame.pack(fill='both', expand=True)
        
        # Load metadata from config
        metadata = self.scope.config.get_metadata_fields()
        if metadata:
            self.update_metadata_fields(metadata)
    
    def add_metadata_field(self, key, value=""):
        """Dynamically add a metadata field to the metadata tab"""
        if key in self.metadata_fields:
            # Field already exists, just update the value
            self.metadata_fields[key][1].set(value)
            return
        
        # Create new row
        row_idx = len(self.metadata_fields)
        ttk.Label(self.metadata_frame, text=f"{key}:").grid(row=row_idx, column=0, sticky='w', pady=5)
        
        # Variable to store the value
        var = tk.StringVar(value=value)
        entry = ttk.Entry(self.metadata_frame, textvariable=var, width=40)
        entry.grid(row=row_idx, column=1, sticky='ew', pady=5, padx=(5, 0))
        
        # Store field references
        self.metadata_fields[key] = (entry, var)
    
    def update_metadata_fields(self, metadata_dict):
        """Update metadata fields based on the provided dictionary"""
        # Clear existing fields
        for widget in self.metadata_frame.winfo_children():
            widget.destroy()
        
        self.metadata_fields = {}
        
        # Add fields from dictionary
        for key, value in metadata_dict.items():
            self.add_metadata_field(key, value)
    
    def scan_for_scope(self):
        """Scan for connected oscilloscope"""
        try:
            # First scan for all available instruments
            self.scope.scan_for_instruments()
            
            # Attempt to auto-connect to a supported scope
            result = self.scope.auto_setup_scope()
            
            if result:
                self.connection_status.config(text="Status: Connected")
                device_info = self.scope.get_device_info()
                self.device_info.config(text=f"Device: {device_info}")
            else:
                self.connection_status.config(text="Status: No supported scope found")
                self.device_info.config(text="No device detected")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scan for scope: {str(e)}")
            self.connection_status.config(text="Status: Error")
            self.device_info.config(text="Error during device scan")
    
    def browse_directory(self):
        """Open file browser to select save directory"""
        directory = filedialog.askdirectory(initialdir=self.save_dir_var.get())
        if directory:
            self.save_dir_var.set(directory)
            # Update config
            self.scope.config.set_save_directory(directory)
    
    def capture_screenshot(self):
        """Capture screenshot from the oscilloscope"""
        if not self.scope.is_connected():
            messagebox.showwarning("Not Connected", "No oscilloscope connected. Please scan for devices first.")
            return
        
        save_dir = self.save_dir_var.get()
        filename = self.filename_var.get()
        bg_color = self.bg_color_var.get()
        save_waveform = self.save_waveform_var.get()
        
        try:
            # Get metadata
            metadata = {key: var.get() for key, (_, var) in self.metadata_fields.items()}
            
            # Capture the screenshot
            file_path = self.scope.capture(
                save_dir, filename, bg_color, save_waveform, metadata
            )
            
            messagebox.showinfo("Success", f"Screenshot saved to: {file_path}")
            
            # Update filename for next capture (increment counter)
            next_filename = self._increment_filename(filename)
            self.filename_var.set(next_filename)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture screenshot: {str(e)}")
    
    def _increment_filename(self, filename):
        """Increment the counter in the filename"""
        # Find the last sequence of digits in the filename
        file_path = Path(filename)
        base = file_path.stem
        ext = file_path.suffix
        match = re.search(r'(\d+)(?!.*\d)', base)
        
        if match:
            # Extract the counter value and its position
            counter_str = match.group(1)
            counter_val = int(counter_str)
            
            # Increment and pad with zeros to maintain the same length
            new_counter = str(counter_val + 1).zfill(len(counter_str))
            
            # Replace the old counter with the new one
            new_base = base[:match.start(1)] + new_counter + base[match.end(1):]
            return new_base + ext
        else:
            # If no counter found, just append _001
            return base + "_001" + ext
