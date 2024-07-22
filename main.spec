a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
             datas=[
                 ('Conexion', 'Conexion'),
                 ('Interfaz', 'Interfaz'),
                 ('Facturas', 'Facturas'),
                 ('Presupuestos', 'Presupuestos'),
                 ('Despacho', 'Despacho'),
                 ('Backup', 'Backup'),
                 ('negocio', 'negocio'),
                 ('.venv', '.venv'),
                 ('resources_rc.py', 'resources_rc.py'),
                 ('credentials.json', '.'),
                 ('token.json', '.'),
                 (r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe', 'bin'),
             ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Gestion2.0',
    icon='Interfaz/Icons/company.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,

)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Gestion2.0')