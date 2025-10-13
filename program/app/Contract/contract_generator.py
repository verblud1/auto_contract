from docxtpl import DocxTemplate
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from pathlib import Path
import locale
from tkinter import messagebox
import sys
import os

from .utils import number_to_words

class ContractGenerator:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        
        # Устанавливаем локаль на случай, если она не установлена в data_manager
        try:
            locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_ALL, 'Russian_Russia.1251')
            except:
                locale.setlocale(locale.LC_ALL, '')

    def generate_contracts(self, common_values, schools_data, school_type, progress_callback=None, log_callback=None):
        """Генерация договоров для всех школ"""
        try:
            if log_callback:
                log_callback("Начало генерации договоров...")

            # Проверяем обязательные параметры
            if not common_values or not schools_data:
                if log_callback:
                    log_callback("Ошибка: отсутствуют необходимые данные")
                return 0, 0

            current_time = datetime.now().strftime("%Y.%m.%d (%H:%M)")
            type_name_ru = "Город" if school_type == "town" else "Район"
            
            new_output_folder_name = f"{type_name_ru} договоры от {current_time}"
            folder_output = self.data_manager.output_dir / new_output_folder_name
            
            # Создание папки с обработкой ошибок
            try:
                folder_output.mkdir(parents=True, exist_ok=True)
                if log_callback:
                    log_callback(f"Создана папка: {folder_output}")
            except Exception as e:
                if log_callback:
                    log_callback(f"Ошибка создания папки: {str(e)}")
                return 0, 0

            # Проверяем доступность школ
            try:
                schools = schools_data[0]["schools"][school_type]
                total_schools = len(schools)
                
                if total_schools == 0:
                    if log_callback:
                        log_callback("Нет школ для обработки")
                    return 0, 0
            except (KeyError, IndexError, TypeError) as e:
                if log_callback:
                    log_callback(f"Ошибка структуры данных школ: {str(e)}")
                return 0, 0
            
            successful_count = 0
            for i, school in enumerate(schools):
                try:
                    if log_callback:
                        log_callback(f"Обработка {school['name']}...")

                    # Пропускаем школы с нулевым количеством детей
                    child_count = school.get('child_count', 0)
                    if child_count <= 0:
                        if log_callback:
                            log_callback(f"Пропуск: {school['name']} (0 детей)")
                        continue

                    # Генерация договора для одной школы
                    result = self.generate_single_contract(
                        common_values, school, folder_output, current_time, log_callback
                    )
                    
                    if result:
                        successful_count += 1
                        if log_callback:
                            log_callback(f"Успешно: {school['name']}")
                    else:
                        if log_callback:
                            log_callback(f"Ошибка: {school['name']}")

                    # Обновление прогресса
                    if progress_callback:
                        progress = (i + 1) / total_schools
                        progress_callback(progress)

                except Exception as e:
                    if log_callback:
                        log_callback(f"Ошибка при обработке {school['name']}: {str(e)}")

            if log_callback:
                log_callback(f"Генерация завершена. Успешно: {successful_count}/{total_schools}")
                
            return successful_count, total_schools

        except Exception as e:
            if log_callback:
                log_callback(f"Критическая ошибка генерации: {str(e)}")
            return 0, 0

    def generate_single_contract(self, common_values, school, output_dir, current_time, log_callback=None):
        """Генерация договора для одной школы"""
        try:
            template_path = self.data_manager.templates_dir / "contracts" / "contract_template.docx"
            
            if not template_path.exists():
                if log_callback:
                    log_callback(f"Шаблон не найден: {template_path}")
                return False

            # Проверяем обязательные поля
            required_fields = ['cost_eat', 'day_count', 'date', 'date_conclusion', 'year']
            for field in required_fields:
                if field not in common_values or not common_values[field]:
                    if log_callback:
                        log_callback(f"Отсутствует обязательное поле: {field}")
                    return False

            # Загрузка шаблона
            try:
                doc = DocxTemplate(template_path)
            except Exception as e:
                if log_callback:
                    log_callback(f"Ошибка загрузки шаблона: {str(e)}")
                return False

            # Расчет стоимости с проверкой значений
            try:
                cost_eat_decimal = Decimal(str(common_values["cost_eat"]))
                day_count_decimal = Decimal(str(common_values["day_count"]))
                child_count_decimal = Decimal(str(school.get('child_count', 0)))

                count_money = cost_eat_decimal * day_count_decimal * child_count_decimal
                count_money = count_money.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                
                # Проверяем, что сумма не отрицательная
                if count_money < 0:
                    if log_callback:
                        log_callback("Ошибка: отрицательная сумма договора")
                    return False
                    
            except (ValueError, TypeError) as e:
                if log_callback:
                    log_callback(f"Ошибка расчета стоимости: {str(e)}")
                return False

            # Преобразование числа в слова
            try:
                decoding_number_words = number_to_words(count_money)
            except Exception as e:
                if log_callback:
                    log_callback(f"Ошибка преобразования числа в слова: {str(e)}")
                decoding_number_words = "ошибка преобразования"

            # Название для договора (убираем недопустимые символы в имени файла)
            invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
            school_name_clean = school['name']
            for char in invalid_chars:
                school_name_clean = school_name_clean.replace(char, '_')
                
            name_doc = f"{school_name_clean} договор от {current_time}.docx"

            # Формирование информации о классификаторах
            classification_info_text = ""
            try:
                if 'bank_account_info' in school and school['bank_account_info']:
                    classification_info_text = "\n".join(
                        f"{info['name']}: {info['value']}"
                        for info in school['bank_account_info'][0].get('classification_info', [])
                    )
            except Exception as e:
                if log_callback:
                    log_callback(f"Ошибка формирования банковской информации: {str(e)}")

            # Создание контекста с безопасным получением значений
            context = {
                'child_count': school.get('child_count', 0), 
                'day_count': common_values["day_count"],
                'cost_eat': locale.format_string('%.2f', common_values["cost_eat"], grouping=True),
                'count_money': locale.format_string('%.2f', float(count_money), grouping=True),
                'decoding_number_words': decoding_number_words, 
                'date': common_values["date"],
                'date_conclusion': common_values["date_conclusion"],
                'year': common_values["year"],
                'contract_number': school.get('contract_number', ''),
                'school_full_name': school.get('school_full_name', ''),
                'school_short_name': school.get('school_short_name', ''),
                'director_full_name': school.get('director_full_name', ''),
                'director_short_name': school.get('director_short_name', ''),
                'postal_code': school.get('postal_code', ''),
                'full_location_school': school.get('full_location_school', ''),
                'personal_account': school.get('bank_account_info', [{}])[0].get('personal_account', ''),
                'INN': school.get('bank_account_info', [{}])[0].get('INN', ''),
                'classification_info': classification_info_text
            }

            # Подстановка значений и сохранение
            try:
                doc.render(context)
                output_path = output_dir / name_doc
                doc.save(output_path)
                
                if log_callback:
                    log_callback(f"Сохранен: {output_path}")
                    
                return True

            except Exception as e:
                if log_callback:
                    log_callback(f"Ошибка сохранения договора: {str(e)}")
                return False

        except Exception as e:
            if log_callback:
                log_callback(f"Общая ошибка генерации договора для {school['name']}: {e}")
            return False