# Single-file executable
pyinstaller --name="Simple_Scope" --noconfirm --onefile --windowed --hidden-import=pyvisa --hidden-import=pyvisa_py --add-data="Simple_Scope/app;app" --add-data="Simple_Scope/tests;tests" Simple_Scope/main.py

# Directory structure
pyinstaller --name="Simple_Scope" --noconfirm --windowed --hidden-import=pyvisa --hidden-import=pyvisa_py --add-data="Simple_Scope/app;app" --add-data="Simple_Scope/tests;tests" Simple_Scope/main.py
