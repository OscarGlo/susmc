# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.building.api import PYZ, EXE
from PyInstaller.building.build_main import Analysis
from PyInstaller.building.datastruct import Tree

block_cipher = None

a = Analysis(['main.py'],
             pathex=['D:\\Oscar\\Programmation\\Python\\susmc'],
             binaries=[], datas=[],
             hiddenimports=[
                 'sklearn.neighbors._typedefs',
                 'sklearn.utils._weight_vector',
                 'sklearn.neighbors._quad_tree'
             ],
             hookspath=[], runtime_hooks=[], excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher, noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, Tree("layers", "layers"),
          [], name='susmc', debug=False, bootloader_ignore_signals=False, strip=False,
          upx=True, upx_exclude=[], runtime_tmpdir=None, console=True)
