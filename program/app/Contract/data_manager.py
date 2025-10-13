import json
import locale
from pathlib import Path
from tkinter import messagebox

class DataManager:
    def __init__(self, base_dir=None):

        #Установка путей до файлов
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        
        #Основные пути
        self.base_dir = base_dir  #родительский (корневой путь проги)
        self.templates_dir = base_dir / "templates" # шаблоны 
        self.output_dir = base_dir / "schools_output" # путь для вывода готовый доков 
        self.data_dir = base_dir / "data" # дата файлы

        # Устанавливаем локаль
        try:
            locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
        except locale.Error:
            locale.setlocale(locale.LC_ALL, '')


    """Загрузка общих значений из common_values.txt"""
    def load_common_values(self):
        
        try:
            values_file_path = self.data_dir / 'common_values.txt'
            
            if not values_file_path.exists():
                return {
                    "cost_eat": 0.0,
                    "day_count": 0,
                    "date": "",
                    "date_conclusion": "",
                    "year": ""
                }

            common_values = {}
            with open(values_file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                            
                        if key == "Стоимость дня":
                            common_values["cost_eat"] = float(value)
                        elif key == "Кол-во дней":
                            common_values["day_count"] = int(value)
                        elif key == "Дата":
                            common_values["date"] = value
                        elif key == "Дата заключения договора":
                            common_values["date_conclusion"] = value
                        elif key == "Год":
                            common_values["year"] = value

            return common_values
            
        except Exception as e:
            print(f"Ошибка загрузки common_values: {e}")
            return {}
        
        
    """Сохранение общих значений в common_values.txt"""
    def save_common_values(self, common_values):
        
        try:
            values_file = self.base_dir.parent / 'common_values.txt'
            with open(values_file, 'w', encoding='utf-8') as f:
                f.write(f"Стоимость дня: {common_values['cost_eat']}\n")
                f.write(f"Кол-во дней: {common_values['day_count']}\n")
                f.write(f"Дата: {common_values['date']}\n")
                f.write(f"Дата заключения договора: {common_values['date_conclusion']}\n")
                f.write(f"Год: {common_values['year']}\n")
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False


    """Загрузка конфигурации школ"""
    def load_schools_config(self):
        
        try:
            config_file = self.data_dir / "config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Ошибка загрузки конфига школ: {e}")
            return None


    """Обновление количества детей для школы"""
    def update_school_child_count(self, schools_data, school_type, school_id, child_count):
       
        try:
            for school in schools_data[0]["schools"][school_type]:
                if school["id"] == school_id:
                    school["child_count"] = child_count
                    return True
            return False
        except Exception as e:
            print(f"Ошибка обновления количества детей: {e}")
            return False