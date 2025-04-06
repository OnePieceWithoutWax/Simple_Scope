"""
PyInstaller hook for PyVISA to ensure all necessary dependencies are included.
Place this file in a 'hooks' directory and reference it in your spec file.
"""
from PyInstaller.utils.hooks import collect_data_files, collect_submodules


# Collect all data files from pyvisa and pyvisa_py
datas = collect_data_files('pyvisa')
datas += collect_data_files('pyvisa_py')

# Collect all submodules to ensure they're included
hiddenimports = collect_submodules('pyvisa')
hiddenimports += collect_submodules('pyvisa_py')
