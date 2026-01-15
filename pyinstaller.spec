#!/bin/bash
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/data/instruments.json', 'data'),
    ],
    hiddenimports=[
        'music21',
        'librosa',
        'sounddevice',
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'scipy',
        'scipy.signal',
        'scipy.interpolate',
        'numpy',
        'resampy',
    ],
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
    [],
    exclude_binaries=True,
    name='MelodyTranscriber',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='arm64',
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MelodyTranscriber',
)

app = BUNDLE(
    coll,
    name='MelodyTranscriber.app',
    icon=None,
    bundle_identifier='com.melodytools.transcriber',
    version='1.0.0',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSMicrophoneUsageDescription': 'MelodyTranscriber needs microphone access to record your singing.',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'LSMinimumSystemVersion': '11.0',
        'NSHighResolutionCapable': True,
    },
)
