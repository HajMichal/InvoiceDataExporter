# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
    ('.env', '.'),  
    ('main.ico', '.'),  
    ],
    hiddenimports=[
        'src.ui',
        'src.core.ai_processor', 
        'src.core.excel_exporter',
        'src.core.get_eur_to_pln_rate',
        'src.core.ocr',
        'src.models.CompanyData',
        'pandas',
        'openpyxl',
        'pytesseract',
        'pdf2image',
        'PIL',
        'google.genai',
        'pydantic',
        'dotenv',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'threading',
        'subprocess'
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
    name='Auto-Faktura',
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
    icon=['main.ico'],
)
