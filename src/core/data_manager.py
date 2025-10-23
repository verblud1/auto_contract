import json
import locale
from pathlib import Path
from tkinter import messagebox
import sys
import re
import os

from core.config import Config

class DataManager:
    def __init__(self):
        # Используем конфигурацию из Config
        self.config = Config()
        
        # Устанавливаем локаль (идентично оригиналу)
        try:
            locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_ALL, 'Russian_Russia.1251')
            except:
                locale.setlocale(locale.LC_ALL, '')

        # Вывод для отладки (идентично оригиналу)
        self.config.print_debug_info()

    # Делегируем методы работы с путями к Config
    def get_template_path(self, template_type="contracts"):
        return self.config.get_template_path(template_type)
    
    def get_output_path(self, output_type="contracts"):
        return self.config.get_output_path(output_type)
    
    def check_template_exists(self):
        return self.config.check_template_exists()

    @property
    def data_dir(self):
        return self.config.data_dir

    @property
    def templates_dir(self):
        return self.config.templates_dir

    @property
    def output_dir(self):
        return self.config.output_dir

    @property
    def resources_dir(self):
        return self.config.resources_dir

    def load_common_values(self):
        """Загрузка общих значений из common_values.txt"""
        try:
            # путь к common values директории
            values_file_path = self.data_dir / 'common_values.txt'
        
            print(f"Ищем common_values.txt по пути: {values_file_path}")
            print(f"Файл существует: {values_file_path.exists()}")
        
            if not values_file_path.exists():
                print("Файл common_values.txt не найден, создаем значения по умолчанию")
                return {
                    "cost_eat": 100.0,
                    "day_count": 30,
                    "date_conclusion": "с 1 сентября по 31 октября 2025 года",
                    "date": "1 сентября 2025 года",
                    "year": "2025"
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
                        elif key == "Дата заключения договора":
                            common_values["date_conclusion"] = value
                        elif key == "Дата":
                            common_values["date"] = value
                        elif key == "Год":
                            common_values["year"] = value
        
            # ВАЖНОЕ ИЗМЕНЕНИЕ: Всегда извлекаем date и year из date_conclusion
            if "date_conclusion" in common_values:
                date_info = self.extract_date_from_period(common_values["date_conclusion"])
                if date_info:
                    # Перезаписываем date и year значениями из периода
                    common_values["date"] = date_info["date"]
                    common_values["year"] = date_info["year"]
                    print(f"Извлекли дату из периода: date='{date_info['date']}', year='{date_info['year']}'")
        
            # Убедимся, что все обязательные поля присутствуют
            default_values = {
                "cost_eat": 100.0,
                "day_count": 30,
                "date_conclusion": "с 1 сентября по 31 октября 2025 года",
                "date": "1 сентября 2025 года",
                "year": "2025"
            }
        
            for key, default_value in default_values.items():
                if key not in common_values:
                    common_values[key] = default_value
                    
            print(f"Загружены common_values: {common_values}")
            return common_values
        
        except Exception as e:
            print(f"Ошибка загрузки common_values: {e}")
            # Возвращаем значения по умолчанию при ошибке
            return {
                "cost_eat": 100.0,
                "day_count": 30,
                "date_conclusion": "с 1 сентября по 31 октября 2025 года",
                "date": "1 сентября 2025 года",
                "year": "2025"
            }

    def extract_date_from_period(self, period_string):
        """Извлекает дату и год из строки периода"""
        try:
            print(f"Извлекаем дату из периода: '{period_string}'")
            
            # Основной паттерн: "с 1 сентября по 31 октября 2025 года"
            pattern = r'с\s+(\d+)\s+(\w+)\s+по\s+\d+\s+\w+\s+(\d{4})\s+года'
            match = re.search(pattern, period_string)
            
            if match:
                day = match.group(1)  # "1"
                month = match.group(2)  # "сентября"
                year = match.group(3)  # "2025"
                
                # Формат даты: "1 сентября 2025 года"
                date = f"{day} {month} {year} года"
                
                print(f"Извлекли: day={day}, month={month}, year={year}, date={date}")
                
                return {
                    "date": date,
                    "year": year
                }
            
            print(f"Не удалось извлечь дату из периода: '{period_string}'")
            return None
            
        except Exception as e:
            print(f"Ошибка извлечения даты из периода: {e}")
            return None
        
    def save_common_values(self, common_values):
        """Сохранение общих значений в common_values.txt"""
        try:
            # Сохраняем в data директории
            values_file_path = self.data_dir / 'common_values.txt'
            
            print(f"Сохраняем common_values в: {values_file_path}")
            
            # ВАЖНОЕ ИЗМЕНЕНИЕ: Перед сохранением убедимся, что date и year синхронизированы с date_conclusion
            if "date_conclusion" in common_values:
                date_info = self.extract_date_from_period(common_values["date_conclusion"])
                if date_info:
                    # Обновляем date и year на основе date_conclusion
                    common_values["date"] = date_info["date"]
                    common_values["year"] = date_info["year"]
                    print(f"Синхронизировали date и year с date_conclusion")
            
            with open(values_file_path, 'w', encoding='utf-8') as f:
                f.write(f"Стоимость дня: {common_values['cost_eat']}\n")
                f.write(f"Кол-во дней: {common_values['day_count']}\n")
                f.write(f"Дата заключения договора: {common_values['date_conclusion']}\n")
                f.write(f"Дата: {common_values.get('date', '1 сентября 2025 года')}\n")
                f.write(f"Год: {common_values.get('year', '2025')}\n")
            
            print("Common_values успешно сохранены")
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False

    def load_schools_config(self):
        """Загрузка конфигурации школ (идентично оригиналу)"""
        try:
            config_file = self.data_dir / "config.json"
            print(f"Ищем config.json по пути: {config_file}")
            print(f"Файл существует: {config_file.exists()}")
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    print("Конфиг школ успешно загружен")
                    return config_data
            else:
                print(f"Файл конфигурации не найден: {config_file}")
                return None
        except Exception as e:
            print(f"Ошибка загрузки конфига школ: {e}")
            return None

    def update_school_child_count(self, schools_data, school_type, school_id, child_count):
        """Обновление количества детей для школы (идентично оригиналу)"""
        try:
            if schools_data and len(schools_data) > 0:
                for school in schools_data[0]["schools"][school_type]:
                    if school["id"] == school_id:
                        school["child_count"] = child_count
                        print(f"Обновлено количество детей для школы {school['name']}: {child_count}")
                        return True
            return False
        except Exception as e:
            print(f"Ошибка обновления количества детей: {e}")
            return False