from docxtpl import DocxTemplate
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from pathlib import Path
import locale
from tkinter import messagebox
import sys
import os

# Исправляем импорт - убираем точку если это не пакет
try:
    from .utils import number_to_words
except ImportError:
    # Альтернативный импорт для случая, когда модуль не является пакетом
    from utils import number_to_words

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
                try:
                    locale.setlocale(locale.LC_ALL, '')
                except:
                    pass  # Если не удалось установить локаль, продолжаем без нее


    def generate_contracts(self):
        """Генерация договоров"""
        try:
            self.generation_tab.clear_log()
            self.generation_tab.log_message("Начало генерации договоров...")
            self.update()

            # Убедимся, что период сохранен перед генерацией
            self.save_period_to_common_values()

            # Проверка заполнения обязательных полей с проверкой наличия ключей
            required_fields = ["cost_eat", "day_count", "date_conclusion", "date", "year"]
            missing_fields = []
            
            for field in required_fields:
                if field not in self.common_values:
                    missing_fields.append(f"{field} (отсутствует ключ)")
                else:
                    value = self.common_values[field].get()
                    if not value:
                        missing_fields.append(field)
            
            if missing_fields:
                messagebox.showwarning("Внимание", f"Заполните все общие параметры! Проблемы с: {', '.join(missing_fields)}")
                return

            if not self.schools_data:
                messagebox.showerror("Ошибка", "Данные о школах не загружены!")
                return

            # Подготовка данных для генерации
            common_values_dict = {}
            for key in required_fields:
                if key in self.common_values:
                    common_values_dict[key] = self.common_values[key].get()
                else:
                    self.generation_tab.log_message(f"Ошибка: ключ '{key}' отсутствует в common_values")
                    messagebox.showerror("Ошибка", f"Отсутствует ключ '{key}' в настройках")
                    return

            def progress_callback(progress):
                self.generation_tab.set_progress(progress)
                self.update()

            def log_callback(message):
                self.generation_tab.log_message(message)
                self.update()

            # Запуск генерации
            successful_count, total_schools = self.contract_generator.generate_contracts(
                common_values_dict,
                self.schools_data,
                self.school_type.get(),
                progress_callback,
                log_callback
            )

            self.generation_tab.log_message(f"\nГенерация завершена! Успешно: {successful_count}/{total_schools}")
            
            if successful_count > 0:
                messagebox.showinfo("Успех", f"Договоры сгенерированы! Успешно: {successful_count}/{total_schools}")
            else:
                messagebox.showwarning("Внимание", "Не удалось сгенерировать ни одного договора!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации: {str(e)}")
            self.generation_tab.log_message(f"Критическая ошибка: {str(e)}\n")


    def generate_single_contract(self, common_values, school, output_dir, current_time, log_callback=None):
        """Генерация договора для одной школы"""
        try:
            template_path = self.data_manager.templates_dir / "contracts" / "contract_template.docx"
            
            if not template_path.exists():
                if log_callback:
                    log_callback(f"Шаблон не найден: {template_path}")
                return False

            # Проверяем обязательные поля с безопасным доступом
            required_fields = ['cost_eat', 'day_count', 'date', 'date_conclusion', 'year']
            for field in required_fields:
                if field not in common_values or common_values.get(field) in [None, ""]:
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
                cost_eat = common_values["cost_eat"]
                day_count = common_values["day_count"]
                child_count = school.get('child_count', 0)
                
                # Преобразуем в Decimal с обработкой ошибок
                cost_eat_decimal = Decimal(str(cost_eat)) if cost_eat else Decimal('0')
                day_count_decimal = Decimal(str(day_count)) if day_count else Decimal('0')
                child_count_decimal = Decimal(str(child_count)) if child_count else Decimal('0')

                count_money = cost_eat_decimal * day_count_decimal * child_count_decimal
                count_money = count_money.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                
                # Проверяем, что сумма не отрицательная
                if count_money < 0:
                    if log_callback:
                        log_callback("Ошибка: отрицательная сумма договора")
                    return False
                    
            except (ValueError, TypeError, Exception) as e:
                if log_callback:
                    log_callback(f"Ошибка расчета стоимости: {str(e)}")
                return False

            # Преобразование числа в слова
            try:
                decoding_number_words = number_to_words(count_money)
            except Exception as e:
                if log_callback:
                    log_callback(f"Ошибка преобразования числа в слова: {str(e)}")
                # Используем запасной вариант
                try:
                    decoding_number_words = f"{count_money} рублей"
                except:
                    decoding_number_words = "сумма прописью"

            # Название для договора (убираем недопустимые символы в имени файла)
            invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
            school_name_clean = school.get('name', 'Школа')
            for char in invalid_chars:
                school_name_clean = school_name_clean.replace(char, '_')
                
            name_doc = f"{school_name_clean} договор от {current_time}.docx"

            # Формирование информации о классификаторах
            classification_info_text = ""
            try:
                bank_account_info = school.get('bank_account_info', [{}])
                if bank_account_info and isinstance(bank_account_info, list) and len(bank_account_info) > 0:
                    classification_info = bank_account_info[0].get('classification_info', [])
                    if classification_info:
                        classification_info_text = "\n".join(
                            f"{info.get('name', '')}: {info.get('value', '')}"
                            for info in classification_info
                            if isinstance(info, dict) and 'name' in info and 'value' in info
                        )
            except Exception as e:
                if log_callback:
                    log_callback(f"Ошибка формирования банковской информации: {str(e)}")

            # Форматирование чисел с учетом локали
            try:
                cost_eat_formatted = locale.format_string('%.2f', float(cost_eat), grouping=True)
            except:
                cost_eat_formatted = str(cost_eat)
                
            try:
                count_money_formatted = locale.format_string('%.2f', float(count_money), grouping=True)
            except:
                count_money_formatted = str(count_money)

            # Создание контекста с безопасным получением значений
            context = {
                'child_count': school.get('child_count', 0), 
                'day_count': common_values.get("day_count", 0),
                'cost_eat': cost_eat_formatted,
                'count_money': count_money_formatted,
                'decoding_number_words': decoding_number_words, 
                'date': common_values.get("date", ""),
                'date_conclusion': common_values.get("date_conclusion", ""),
                'year': common_values.get("year", ""),
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
                log_callback(f"Общая ошибка генерации договора для {school.get('name', 'неизвестная школа')}: {e}")
            return False