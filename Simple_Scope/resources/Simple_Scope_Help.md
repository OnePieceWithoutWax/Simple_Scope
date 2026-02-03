# Simple Scope Help

Simple Scope is a tool for capturing screenshots from your oscilloscope and saving them to your computer.

---

## Capture Tab

The Capture tab is where you configure and trigger screenshot captures from your oscilloscope.

### Layout Modes

At the top of the Capture tab, you can select from three layout modes:

- **Basic**: Simple layout with save directory and filename fields. Best for quick captures without complex folder organization.

- **Engineering**: Pre-configured subdirectory structure with labeled fields for "IC Part Number" and "Test". Useful for organizing captures by project and test type.

- **Advanced**: Flexible subdirectory builder that lets you add multiple rows of subdirectories with custom naming. Each row can have multiple text fields that get joined with underscores.

### Controls

| Control | Description |
|---------|-------------|
| **Browse** | Opens a file browser to select the save directory |
| **Save Directory** | The folder where captured images will be saved |
| **Filename** | Base filename for the captured image (extension added automatically) |
| **Capture** | Captures a screenshot from the connected oscilloscope and saves it |
| **Copy to Clipboard** | Copies the most recently captured image to the clipboard |

### Subdirectory Controls (Engineering & Advanced Layouts)

| Control | Description |
|---------|-------------|
| **+** | Adds another text field to the current subdirectory row (fields are joined with underscores) |
| **-** | Removes the last text field from the current subdirectory row |
| **+ Add Row** | (Advanced only) Adds a new subdirectory level |
| **X** | (Advanced only) Removes the entire subdirectory row |

### Image Preview

If enabled in Config, a preview of the captured image will be displayed either to the right of or below the capture controls.

---

## Scope Tab

The Scope tab manages your oscilloscope connection.

### Connection Status

Shows the current connection state:
- **Not Connected**: No oscilloscope is currently connected
- **Connected**: Successfully connected to an oscilloscope
- **No supported scope found**: Scan completed but no compatible device was detected
- **Error**: An error occurred during connection

### Discovered Instruments

A dropdown list showing all instruments found during the scan. Select an instrument from this list to connect to it.

### Controls

| Control | Description |
|---------|-------------|
| **Scan for Scope** | Searches for connected oscilloscopes via USB/VISA. The application will attempt to auto-connect to a supported device. |

### Currently Connected

Displays information about the currently connected oscilloscope including:
- Model number
- Serial number (if available)
- Connection address

---

## Config Tab

The Config tab contains settings that control capture behavior and file naming.

### File Settings

| Setting | Description |
|---------|-------------|
| **File Format** | Image format for saved screenshots (currently PNG) |
| **Background** | Background color for the captured image (white or black) |

### Filename Options

| Setting | Description |
|---------|-------------|
| **Auto increment filename** | Automatically appends a number (_001, _002, etc.) to the filename and increments after each capture. Cannot be used with datestamp. |
| **Append datestamp to filename** | Adds a timestamp (_YYYY.MM.DD_HH.MM.SS) to each filename. Cannot be used with auto increment. |

**Note**: Auto increment and datestamp are mutually exclusive - enabling one will disable the other.

### Data Options

| Setting | Description |
|---------|-------------|
| **Save waveform data** | (Not yet implemented) When enabled, saves waveform data alongside the screenshot |

### Display Options

| Setting | Description |
|---------|-------------|
| **Display Captured Image** | Controls whether and where to show the captured image preview. Options: Disabled, Display To The Right, Display Below |
| **Display Image Size** | Size of the image preview. Options: Small, Medium, Large |

### Clipboard Options

| Setting | Description |
|---------|-------------|
| **Auto copy to clipboard after capture** | Automatically copies the captured image to the clipboard after each capture |

---

## Troubleshooting

If you're having issues capturing screenshots, follow these steps:

### 1. Check Oscilloscope Connection

- Ensure your oscilloscope is powered on and connected to your computer via USB
- Go to the **Scope** tab and click **Scan for Scope**
- Verify your oscilloscope appears in the **Discovered Instruments** dropdown

### 2. Verify Connection Status

- The **Status** should show "Connected"
- The **Currently Connected** section should display your oscilloscope model and address
- If it shows "No supported scope found", your oscilloscope model may not be supported

### 3. Check Save Directory

- Make sure the **Save Directory** exists and is writable
- Use the **Browse** button to select a valid directory
- Ensure you have write permissions to the selected folder

### 4. Verify Filename

- The **Filename** field should not be empty
- Avoid using special characters that aren't allowed in filenames (/, \, :, *, ?, ", <, >, |)

### 5. Try a Manual Capture

- If auto-connect fails, manually select your oscilloscope from the **Discovered Instruments** dropdown
- Wait for the status to show "Connected" before attempting to capture

### 6. Check the Application Log

If issues persist, check the application log for error messages:

1. Go to the **Help** tab
2. Check the **Show Application Log** checkbox
3. Review the log entries for any error messages
4. Use the **Save Log** button to save the log file for further analysis or when reporting issues

### Common Issues

| Issue | Solution |
|-------|----------|
| "No oscilloscope connected" warning | Click Scan for Scope on the Scope tab |
| Oscilloscope not found | Check USB connection, try a different USB port |
| Capture fails | Check that the scope is not in a busy state (e.g., single trigger waiting) |
| Image not displaying | Enable image display in Config tab settings |
| Permission denied saving file | Choose a different save directory with write access |

---

For additional help, bug reports, or feature requests, please visit the project repository linked in the **About** tab.
