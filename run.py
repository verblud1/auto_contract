import sys
from pathlib import Path

# Добавляем src в PYTHONPATH
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from gui.main_window import MainWindow

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()