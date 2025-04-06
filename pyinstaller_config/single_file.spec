# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
import os

block_cipher = None

# Get the base path of the project
base_path = Path(os.path.abspath(SPECPATH)).parent

# Data files to include
data_files = [
    (str(base_path / 'Simple_Scope' / 'app'), 'app'),
    (str(base_path / 'Simple_Scope' / 'tests'), 'tests'),
]

# Add any additional files or directories that need to be included
added_files = []

a = Analysis(
    [str(base_path / 'Simple_Scope' / 'main.py')],
    pathex=[str(base_path)],
    binaries=[],
    datas=data_files + added_files,
    hiddenimports=['pyvisa', 'pyvisa_py'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Simple_Scope',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add an icon path here if you have one
)
