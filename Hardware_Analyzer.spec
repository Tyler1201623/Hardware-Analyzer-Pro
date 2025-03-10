# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ('src/static/*', 'src/static'),
    ('src/templates/*', 'src/templates'), 
    ('src/core/*.py', 'src/core'),
    ('src/core/*.json', 'src/core'),
    ('favicon.ico', '.'),
    ('LICENSE', '.'),
    ('README.md', '.'),
    ('settings.json', '.'),
]

a = Analysis(
    ['src/main.py'],  # Point directly to main.py
    pathex=[
        'src',
        'src/core'
    ],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'matplotlib.backends.backend_qt5agg',
        'numpy',
        'psutil',
        'py3nvml',
        'wmi',
        'win32com.client',
        'darkdetect',
        'reportlab',
        'src.core.hardware_manager',
        'src.core.network',
        'src.core.utils',
        'src.core.cpu',
        'src.core.ram',
        'src.core.gpu',
        'src.core.storage',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'test'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Hardware Analyzer Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='favicon.ico',
    version='file_version_info.txt',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Hardware Analyzer Pro',
)
