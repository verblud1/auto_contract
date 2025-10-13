import sys
import os
from pathlib import Path
import customtkinter as ctk

class ContractAuto_App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Функция для получения корректных путей в PyInstaller
        def resource_path(relative_path):
            """Возвращает корректный путь для доступа к ресурсам"""
            try:
                # PyInstaller создает временную папку _MEIPASS
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            
            return os.path.join(base_path, relative_path)
        
        # Сохраняем функцию как атрибут класса, чтобы использовать в других методах
        self.resource_path = resource_path
        
        # Теперь инициализируем пути с помощью этой функции
        self.setup_paths()
        
        # Остальная инициализация...
        self.create_widgets()
        self.load_data()

    def setup_paths(self):
        """Настройка всех путей приложения"""
        # Основные директории
        if getattr(sys, 'frozen', False):
            # Если приложение собрано PyInstaller
            self.base_dir = Path(sys.executable).parent
        else:
            # Если запущено из исходного кода
            self.base_dir = Path(__file__).parent.parent
        
        # Пути к ресурсам
        self.templates_dir = Path(self.resource_path("templates"))
        self.data_dir = Path(self.resource_path("data"))
        
        # Выходная директория - создается рядом с исполняемым файлом
        self.output_dir = self.base_dir / "schools_output"
        
        # Создаем выходную директорию, если её нет
        self.output_dir.mkdir(exist_ok=True)
        
        print(f"Base dir: {self.base_dir}")
        print(f"Templates dir: {self.templates_dir}")
        print(f"Data dir: {self.data_dir}")
        print(f"Output dir: {self.output_dir}")