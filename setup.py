from PyInstaller.__main__ import run

if __name__ == '__main__':
    opts = [
        'run.py',
        '--onefile',
        '--name=AutoContract',
        '--add-data=src/templates;templates',
        '--add-data=data;data',
        '--add-data=resources;resources',
        '--icon=resources/icon.ico',
        '--windowed'
    ]
    run(opts)