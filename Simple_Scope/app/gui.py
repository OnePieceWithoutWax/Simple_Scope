"""
GUI implementation for the Oscilloscope Screenshot Capture Application
"""

from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from app.simple_scope import SimpleScope
from app.utils import increment_filename, filename_with_datestamp

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
        self.scope_tab = ttk.Frame(self.notebook)  # Previously setup_tab
        self.capture_tab = ttk.Frame(self.notebook)  # Previously main_tab
        self.config_tab = ttk.Frame(self.notebook)
        self.metadata_tab = ttk.Frame(self.notebook)
        self.metadata_fields = {}

        # Layout mode variable
        self.layout_mode_var = tk.StringVar(value="Basic")

        self.notebook.add(self.capture_tab, text="Capture")
        self.notebook.add(self.config_tab, text="Config")
        self.notebook.add(self.scope_tab, text="Scope")

        # self.notebook.add(self.metadata_tab, text="Metadata")
        # Initialize the tabs
        self._initialize_scope_tab()
        self._initialize_capture_tab()
        self._initialize_config_tab()
        # self._initialize_metadata_tab()
        
        # Auto-scan for scope on startup
        self.after(500, self.scan_for_scope)
    
    def _initialize_scope_tab(self):
        """Initialize the Scope tab with connection controls"""
        frame = ttk.Frame(self.scope_tab, padding=(20, 10))
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
    
    def _initialize_capture_tab(self):
        """Initialize the Capture tab with layout selector and capture controls"""
        # Layout selector at top
        layout_frame = ttk.Frame(self.capture_tab, padding=(20, 10))
        layout_frame.pack(fill='x')

        ttk.Label(layout_frame, text="Layout:").pack(side='left', padx=(0, 10))

        basic_btn = ttk.Radiobutton(layout_frame, text="Basic",
                                    variable=self.layout_mode_var, value="Basic",
                                    command=self._redraw_capture_content)
        basic_btn.pack(side='left', padx=(0, 10))

        engineering_btn = ttk.Radiobutton(layout_frame, text="Engineering",
                                          variable=self.layout_mode_var, value="Engineering",
                                          command=self._redraw_capture_content)
        engineering_btn.pack(side='left')

        # Separator
        ttk.Separator(self.capture_tab, orient='horizontal').pack(fill='x', padx=20)

        # Content frame that will be redrawn based on layout
        self.capture_content_frame = ttk.Frame(self.capture_tab)
        self.capture_content_frame.pack(fill='both', expand=True)

        # Initialize variables used by capture
        self.save_dir_var = tk.StringVar(value=self.scope.config.get_save_directory())
        self.filename_var = tk.StringVar(value=self.scope.config.get_default_filename())

        # Draw initial content
        self._redraw_capture_content()

    def _redraw_capture_content(self):
        """Redraw the capture tab content based on selected layout"""
        # Clear existing content
        for widget in self.capture_content_frame.winfo_children():
            widget.destroy()

        layout = self.layout_mode_var.get()

        if layout == "Basic":
            self._draw_basic_layout()
        else:
            self._draw_engineering_layout()

    def _draw_basic_layout(self):
        """Draw the Basic layout for capture tab"""
        frame = ttk.Frame(self.capture_content_frame, padding=(20, 10))
        frame.pack(fill='both', expand=True)

        # Browse button
        browse_button = ttk.Button(frame, text="Browse", command=self.browse_directory)
        browse_button.grid(row=0, column=1, sticky='w', pady=5, padx=(5, 0))

        # Save Directory
        ttk.Label(frame, text="Save Directory:").grid(row=1, column=0, sticky='w', pady=5)
        save_dir_entry = ttk.Entry(frame, textvariable=self.save_dir_var, width=80)
        save_dir_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=(5, 0))

        # Filename
        ttk.Label(frame, text="Filename:").grid(row=2, column=0, sticky='w', pady=5)
        filename_entry = ttk.Entry(frame, textvariable=self.filename_var, width=40)
        filename_entry.grid(row=2, column=1, sticky='ew', pady=5, padx=(5, 0))

        # Capture button
        capture_button = ttk.Button(frame, text="Capture", command=self.capture_screenshot)
        capture_button.grid(row=3, column=0, columnspan=3, sticky='w', pady=10)

    def _draw_engineering_layout(self):
        """Draw the Engineering layout for capture tab (placeholder)"""
        frame = ttk.Frame(self.capture_content_frame, padding=(20, 10))
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Engineering layout - Coming soon").pack(pady=20)

    def _initialize_config_tab(self):
        """Initialize the Config tab with file format, background, and waveform settings"""
        frame = ttk.Frame(self.config_tab, padding=(20, 10))
        frame.pack(fill='both', expand=True)

        # File format
        ttk.Label(frame, text="File Format:").grid(row=0, column=0, sticky='w', pady=5)

        self.file_format_var = tk.StringVar(value="png")
        file_format_combo = ttk.Combobox(frame, textvariable=self.file_format_var,
                                         values=["png"], state="readonly", width=10)
        file_format_combo.grid(row=0, column=1, sticky='w', pady=5, padx=(5, 0))

        # Background color
        ttk.Label(frame, text="Background:").grid(row=1, column=0, sticky='w', pady=5)

        self.bg_color_var = tk.StringVar(value="white")
        bg_color_combo = ttk.Combobox(frame, textvariable=self.bg_color_var,
                                     values=["white", "black"], state="readonly", width=10)
        bg_color_combo.grid(row=1, column=1, sticky='w', pady=5, padx=(5, 0))

        # Save waveform data
        self.save_waveform_var = tk.BooleanVar(value=False)
        save_waveform_check = ttk.Checkbutton(frame, text="Save waveform data",
                                             variable=self.save_waveform_var)
        save_waveform_check.grid(row=2, column=0, columnspan=2, sticky='w', pady=10)

        # Auto increment filename
        self.auto_increment_var = tk.BooleanVar(value=self.scope.config.get_auto_increment())
        self.auto_increment_check = ttk.Checkbutton(frame, text="Auto increment filename",
                                                    variable=self.auto_increment_var,
                                                    command=self._on_auto_increment_changed)
        self.auto_increment_check.grid(row=3, column=0, columnspan=2, sticky='w', pady=5)

        # Datestamp filename
        self.datestamp_var = tk.BooleanVar(value=self.scope.config.get_datestamp())
        self.datestamp_check = ttk.Checkbutton(frame, text="Append datestamp to filename",
                                               variable=self.datestamp_var,
                                               command=self._on_datestamp_changed)
        self.datestamp_check.grid(row=4, column=0, columnspan=2, sticky='w', pady=5)

    def _on_auto_increment_changed(self):
        """Handle auto increment checkbox change - mutually exclusive with datestamp"""
        if self.auto_increment_var.get():
            self.datestamp_var.set(False)
        self.scope.config.set_auto_increment(self.auto_increment_var.get())

    def _on_datestamp_changed(self):
        """Handle datestamp checkbox change - mutually exclusive with auto increment"""
        if self.datestamp_var.get():
            self.auto_increment_var.set(False)
        self.scope.config.set_datestamp(self.datestamp_var.get())
        
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

        try:
            filename_ = self.filename_var.get()

            # Apply datestamp if enabled
            if self.datestamp_var.get():
                filename_ = filename_with_datestamp(filename_)

            # Capture the screenshot
            file_path = self.scope.capture(save_dir = self.save_dir_var.get(),
                                            filename = filename_,
                                            suffix = self.file_format_var.get(),
                                            bg_color = self.bg_color_var.get(),
                                            save_waveform = self.save_waveform_var.get(),
                                            metadata = {key: var.get() for key, (_, var) in self.metadata_fields.items()}
                                            )

            # Update filename for next capture if auto increment is enabled
            if self.auto_increment_var.get():
                self.filename_var.set(increment_filename(self.filename_var.get()))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture screenshot: {str(e)}")
