import os
import cx_Freeze
os.environ['QML2_IMPORT_PATH'] = r'C:\Users\redmi\AppData\Local\Programs\Python\Python312\Lib\site-packages\PyQt5\Qt5\qml'
os.environ['QT_PLUGIN_PATH'] = r'C:\Users\redmi\AppData\Local\Programs\Python\Python312\Lib\site-packages\PyQt5\Qt5\plugins'

executables = [cx_Freeze.Executable(
    "ds.py",
    # base="Win32GUI",
    target_name="tic_tac_toe.exe"
)]

cx_Freeze.setup(
    name="Крестики-нолики",
    version="1.0",
    options={"build_exe": {
        # 'include_msvcr': True,
        "packages": ["PyQt5", "sqlite3", "datetime"],
        "zip_include_packages": ["PyQt5", "sqlite3"],
        "include_files": [
            'cat.png',
            'rules.txt',
            'rules1.txt',
            'game_stats.db',
            ( r'C:\Users\redmi\AppData\Local\Programs\Python\Python312\Lib\site-packages\PyQt5\Qt5\plugins\platforms', "platforms"),

            (r'C:\Users\redmi\AppData\Local\Programs\Python\Python312\Lib\site-packages\PyQt5\Qt5\qml', "qml"),
        ],
        "excludes": []
    }},
    executables=executables
)
