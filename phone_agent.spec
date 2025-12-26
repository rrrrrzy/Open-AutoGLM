# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller configuration for Phone Agent.

Usage:
    pyinstaller phone_agent.spec

This will create a standalone executable in the dist/ directory.
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all data files from resources directory
datas = [
    ('image.png', '.'),  # System tray icon
    ('resources', 'resources'),  # Privacy policies and other resources
]

# Collect all phone_agent submodules
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'openai',
    'PIL',
    'PIL.Image',
    'requests',
    'phone_agent',
    'phone_agent.adb',
    'phone_agent.adb.connection',
    'phone_agent.adb.device',
    'phone_agent.adb.input',
    'phone_agent.adb.screenshot',
    'phone_agent.hdc',
    'phone_agent.hdc.connection',
    'phone_agent.hdc.device',
    'phone_agent.hdc.input',
    'phone_agent.hdc.screenshot',
    'phone_agent.xctest',
    'phone_agent.xctest.connection',
    'phone_agent.xctest.device',
    'phone_agent.xctest.input',
    'phone_agent.xctest.screenshot',
    'phone_agent.config',
    'phone_agent.config.apps',
    'phone_agent.config.apps_harmonyos',
    'phone_agent.config.apps_ios',
    'phone_agent.config.i18n',
    'phone_agent.config.prompts',
    'phone_agent.config.prompts_en',
    'phone_agent.config.prompts_zh',
    'phone_agent.config.timing',
    'phone_agent.actions',
    'phone_agent.actions.handler',
    'phone_agent.actions.handler_ios',
    'phone_agent.model',
    'phone_agent.model.client',
    'phone_agent.agent',
    'phone_agent.agent_ios',
    'phone_agent.device_factory',
    'phone_agent.subprocess_utils',
    'ui',
    'ui.main_window',
    'ui.settings',
    'ui.scheduler',
    'ui.resource_path',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'numpy.testing',
        'setuptools',
    ],
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
    name='PhoneAgent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Hide console window - GUI only
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='image.png',  # Application icon
)

# For macOS: Create .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='PhoneAgent.app',
        icon='image.png',
        bundle_identifier='com.phoneagent.app',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
        },
    )
