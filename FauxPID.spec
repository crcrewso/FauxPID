# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project_dir = Path.cwd()
entry_script = project_dir / "FauxPID" / "app" / "main.py"
resources_dir = project_dir / "resources"


a = Analysis(
    [str(entry_script)],
    pathex=[str(project_dir)],
    binaries=[],
    datas=[(str(resources_dir), "resources")],
    hiddenimports=[
        "FauxPID.app.analysis_gui",
        "FauxPID.images.create_image",
        "FauxPID.utils.dicom_analysis",
        "FauxPID.utils.dicom_metadata",
        "FauxPID.utils.resource_staging",
        "FauxPID.algorithms.metrics",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="FauxPID",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
