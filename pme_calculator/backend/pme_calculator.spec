# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

# Get the current directory and project paths
current_dir = Path.cwd()
project_root = current_dir.parent  # pme_calculator directory
frontend_dist = project_root / 'frontend' / 'dist'
pme_app_dir = project_root / 'pme_app'

# Define data files to include
datas = []

# Include the built React frontend
if frontend_dist.exists():
    datas.append((str(frontend_dist), 'frontend/dist'))

# Include the pme_app module and its subdirectories
if pme_app_dir.exists():
    # Add the entire pme_app directory
    for root, dirs, files in os.walk(pme_app_dir):
        for file in files:
            if file.endswith(('.py', '.csv', '.xlsx', '.json')):
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, project_root)
                dest_path = os.path.dirname(rel_path)
                datas.append((src_path, dest_path))

# Define hidden imports (modules that PyInstaller might miss)
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'pandas',
    'numpy',
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.backends.backend_tkagg',
    'openpyxl',
    'xlrd',
    'scipy',
    'scipy.optimize',
    'webview',
    'webview.platforms.cocoa',  # macOS specific
    'webview.platforms.gtk',    # Linux specific  
    'webview.platforms.winforms', # Windows specific
    'pme_app',
    'pme_app.utils',
    'pme_app.pme_calcs',
    'pme_app.gui',
    'pme_app.gui.main_window',
]

# Analysis configuration
a = Analysis(
    ['main.py'],
    pathex=[str(current_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'test',
        'tests',
        'testing',
        'unittest',
        'doctest',
        'pdb',
        'pydoc',
        'tkinter.test',
    ],
    noarchive=False,
    optimize=0,
)

# Remove duplicate entries
pyz = PYZ(a.pure)

# Executable configuration
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PME_Calculator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for windowed app (no console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
)

# Optional: Create a macOS app bundle (.app)
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='PME Calculator.app',
        icon=None,  # Add icon path here if you have one
        bundle_identifier='com.pme.calculator',
        info_plist={
            'CFBundleName': 'PME Calculator',
            'CFBundleDisplayName': 'PME Calculator',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
        }
    ) 