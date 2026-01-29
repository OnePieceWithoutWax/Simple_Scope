# Claude Code Guidelines for Simple_Scope

## Architecture

### SimpleScope Class
The `SimpleScope` class (`app/simple_scope.py`) is the core backend and should be able to **operate standalone** (e.g., in Jupyter notebooks, scripts, or other applications) without requiring the GUI. All logic should be implemented here, and not in the gui layer

Key design principles:
- `SimpleScope` handles all oscilloscope operations: connection, capture, and file saving
- It manages configuration via `AppConfig`
- It should not depend on any GUI components

### GUI Layer
The GUI (`app/gui.py`) should **only expose the API defined in SimpleScope**. It is a thin wrapper that:
- Provides a user interface for SimpleScope functionality
- Reads/writes settings to the config
- Does not implement core logic directly

### Configuration
`AppConfig` (`app/config.py`) handles persistent settings:
- `auto_increment`: Auto-increment filename after each capture
- `datestamp`: Append timestamp to filename (mutually exclusive with auto_increment)
- `save_directory`, `default_filename`, `file_format`, `background_color`, `save_waveform`

## File Naming Options
Both options can be off, but they are **mutually exclusive** (both cannot be on):
- **Auto Increment**: Appends `_001`, `_002`, etc. and increments after each capture
- **Datestamp**: Appends `_YYYY.MM.DD_HH.MM.SS` timestamp to each capture

