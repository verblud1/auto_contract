import sys
from pathlib import Path

class Config:
    """Конфигурация приложения с логикой идентичной оригинальному DataManager"""
    
    def __init__(self):
        # Полностью идентичная логика определения base_dir как в оригинальном DataManager
        if getattr(sys, 'frozen', False):
            # Режим PyInstaller
            self.base_dir = Path(sys.executable).parent
        else:
            # Режим разработки
            self.base_dir = Path(__file__).parent.parent.parent
        
        # Основные пути (идентично оригиналу)
        self.data_dir = self.base_dir / "data"
        self.templates_dir = self.base_dir / "templates"
        self.output_dir = self.base_dir / "outputs"
        self.resources_dir = self.base_dir / "resources"
        
        # Создаем необходимые директории (идентично оригиналу)
        self._create_directories()

        # Списки для выпадающих списков (для UI)
        self.days = [str(i) for i in range(1, 32)]
        self.months = [
            "января", "февраля", "марта", "апреля", "мая", "июня",
            "июля", "августа", "сентября", "октября", "ноября", "декабря"
        ]

    def _create_directories(self):
        """Создает необходимые директории (идентично оригинальному DataManager)"""
        self.data_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self.resources_dir.mkdir(exist_ok=True)

    def get_template_path(self, template_type="contracts"):
        """Возвращает путь к шаблонам по типу (идентично оригиналу)"""
        return self.templates_dir / template_type
    
    def get_output_path(self, output_type="contracts"):
        """Возвращает путь для выходных файлов по типу (идентично оригиналу)"""
        path = self.output_dir / output_type
        path.mkdir(exist_ok=True)
        return path

    def print_debug_info(self):
        """Вывод отладочной информации (идентично оригиналу)"""
        print(f"Base dir: {self.base_dir}")
        print(f"Data dir: {self.data_dir}")
        print(f"Templates dir: {self.templates_dir}")
        print(f"Output dir: {self.output_dir}")

    def check_template_exists(self):
        """Проверка существования шаблона договора (идентично оригиналу)"""
        template_path = self.templates_dir / "contracts" / "contract_template.docx"
        exists = template_path.exists()
        print(f"Шаблон договора существует: {exists} (путь: {template_path})")
        return exists