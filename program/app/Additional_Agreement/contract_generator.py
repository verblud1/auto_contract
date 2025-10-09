from docxtpl import DocxTemplate
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from pathlib import Path
import locale
from tkinter import messagebox

from .utils import number_to_words

class ContractGenerator:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def generate_contracts(self, common_values, schools_data, school_type, progress_callback=None, log_callback=None):
        """Генерация договоров для всех школ"""
        try:
            if log_callback:
                log_callback("Начало генерации договоров...")

            current_time = datetime.now().strftime("%Y.%m.%d (%H:%M)")
            type_name_ru = "Город" if school_type == "town" else "Район"
            
            new_output_folder_name = f"{type_name_ru} договоры от {current_time}"
            folder_output = self.data_manager.output_dir / new_output_folder_name
            
            # Создание папки
            folder_output.mkdir(parents=True, exist_ok=True)

            schools = schools_data[0]["schools"][school_type]
            total_schools = len(schools)
            
            successful_count = 0
            for i, school in enumerate(schools):
                try:
                    if log_callback:
                        log_callback(f"Обработка {school['name']}...")

                    # Генерация договора для одной школы
                    result = self.generate_single_contract(
                        common_values, school, folder_output, current_time
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

            return successful_count, total_schools

        except Exception as e:
            if log_callback:
                log_callback(f"Критическая ошибка генерации: {str(e)}")
            return 0, 0

    def generate_single_contract(self, common_values, school, output_dir, current_time):
        """Генерация договора для одной школы"""
        try:
            template_path = self.data_manager.templates_dir / "contracts" / "contract_template.docx"
            
            if not template_path.exists():
                return False

            # Загрузка шаблона
            doc = DocxTemplate(template_path)

            # Расчет стоимости
            cost_eat_decimal = Decimal(str(common_values["cost_eat"]))
            day_count_decimal = Decimal(str(common_values["day_count"]))
            child_count_decimal = Decimal(str(school.get('child_count', 0)))

            count_money = cost_eat_decimal * day_count_decimal * child_count_decimal
            count_money = count_money.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            decoding_number_words = number_to_words(count_money)

            # Название для договора
            name_doc = f"{school['name']} договор от {current_time}.docx"

            # Формирование информации о классификаторах
            classification_info_text = ""
            if 'bank_account_info' in school and school['bank_account_info']:
                classification_info_text = "\n".join(
                    f"{info['name']}: {info['value']}"
                    for info in school['bank_account_info'][0].get('classification_info', [])
                )

            # Создание контекста
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
            doc.render(context)
            output_path = output_dir / name_doc
            doc.save(output_path)
            
            return True

        except Exception as e:
            print(f"Ошибка генерации договора для {school['name']}: {e}")
            return False