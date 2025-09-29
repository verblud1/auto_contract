# разделить на функцию старта и чтения и всего такого и основной функции
# сделать сохранения  в конфиг child_count 
# добавить возможность добалвения в конфиг пользователем для каждой школы()
# сделать чтобы у пользователя запрашивалось по каждой школе про обучающихся с 1-5, c 5-11 классы то есть по классам чтобы пользователь вводил а потом все это суммировалось. в итоге вместо child_count в конфиге будут по классам в каждой школе
# в будущем добавить возможность добавлять школы из интерфейса
# добавить комментарии
# ADDITIONAL contract FUNC
# допники добавить(создание отдельных договоров)
# добавить обработчики ошибок
# добавить проверку try except 
# добавить возможность очистки папки вывода от старых решений
# чтобы прога была вроде exe и можно было бы скачать с гитхаба
# возможно, добавить ui
# добавить файл с зависимостями
# добавить чтобы 0 в ui был как плейсхолдер
# Добавить функциональность для ввода данных по классам
# Реализовать сохранение измененных данных о школах в config.json
# Добавить возможность добавления новых школ через интерфейс
# Создать систему обработки ошибок с более детальной информацией
# Добавить возможность выбора шаблонов
# улучшить и упростить вписывание данных из коммон валуес
# добавить выбор цвета пользователем и настройку проги
# exe добавить

from docxtpl import DocxTemplate
from num2words import num2words
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import locale
import json
import sys
import os 

import customtkinter as ctk
from tkinter import messagebox

class ContractAuto_App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Настройка основного окна
        self.title("Авто Договор")
        self.geometry("1000x700")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        #variables / find directions to files
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.script_dir = Path(__file__).parent
        self.parent_dir = self.script_dir.parent

        self.templates_dir = self.parent_dir / "templates"
        self.output_dir = self.parent_dir.parent / "schools_output"

        # Исправление: инициализация переменных состояния
        self.school_type = ctk.StringVar(value="town")  # Добавлено значение по умолчанию
        self.type_name_ru = ""

        self.common_values = {
            "cost_eat": ctk.DoubleVar(value=0.0),
            "day_count": ctk.IntVar(value=0),
            "date": ctk.StringVar(value=""),
            "date_conclusion": ctk.StringVar(value=""),
            "year": ctk.StringVar(value="")
        }

        # Устанавливаем русскую локаль для корректного форматирования чисел
        try:
            locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
        except locale.Error:
            # Fallback на системную локаль если русская недоступна
            locale.setlocale(locale.LC_ALL, '')

        # Исправление: перенес создание виджетов до загрузки данных
        self.create_widgets()
        self.load_data()


    def create_widgets(self):
        # Создание вкладок
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Добавление вкладок
        self.tabview.add("Общие настройки")
        self.tabview.add("Школы")
        self.tabview.add("Генерация")
        
        # Настройка вкладок
        self.setup_general_tab()
        self.setup_schools_tab()
        self.setup_generation_tab()

    def setup_general_tab(self):
        tab = self.tabview.tab("Общие настройки")
        
        # Поля для общих значений
        labels = ["Стоимость питания (руб):", "Количество дней:", "Дата:", "Дата заключения:", "Год:"]
        keys = ["cost_eat", "day_count", "date", "date_conclusion", "year"]
        
        for i, (label, key) in enumerate(zip(labels, keys)):
            ctk.CTkLabel(tab, text=label).grid(row=i, column=0, padx=10, pady=10, sticky="w")
            entry = ctk.CTkEntry(tab, textvariable=self.common_values[key])
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")

        # Кнопки загрузки/сохранения
        btn_frame = ctk.CTkFrame(tab)
        btn_frame.grid(row=len(labels), column=0, columnspan=2, pady=20)
        
        ctk.CTkButton(btn_frame, text="Загрузить из файла", command=self.load_values).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Сохранить в файл", command=self.save_values).pack(side="left", padx=10)
        
        tab.grid_columnconfigure(1, weight=1)

    def setup_schools_tab(self):
        tab = self.tabview.tab("Школы")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # Выбор типа школ
        type_frame = ctk.CTkFrame(tab)
        type_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(type_frame, text="Тип школ:").pack(side="left", padx=10)
        ctk.CTkRadioButton(type_frame, text="Город", variable=self.school_type, 
                          value="town", command=self.update_schools_display).pack(side="left", padx=10)
        ctk.CTkRadioButton(type_frame, text="Район", variable=self.school_type, 
                          value="district", command=self.update_schools_display).pack(side="left", padx=10)
        
        # Таблица школ
        self.schools_table_frame = ctk.CTkScrollableFrame(tab)
        self.schools_table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.schools_table_frame.grid_columnconfigure(0, weight=1)

    def setup_generation_tab(self):
        tab = self.tabview.tab("Генерация")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # Лог генерации
        ctk.CTkLabel(tab, text="Лог выполнения:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.log_text = ctk.CTkTextbox(tab, height=200)
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Прогресс бар
        self.progress_bar = ctk.CTkProgressBar(tab)
        self.progress_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        self.progress_bar.set(0)
        
        # Кнопка генерации
        ctk.CTkButton(tab, text="Сгенерировать договоры", command=self.generate_contracts,
                     fg_color="green", hover_color="dark green").grid(row=3, column=0, pady=20)
        
    def update_schools_display(self):
        # Очистка предыдущего отображения
        for widget in self.schools_table_frame.winfo_children():
            widget.destroy()
      
        # Заголовки таблицы
        headers = ["Школа", "Кол-во детей"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(self.schools_table_frame, text=header, font=ctk.CTkFont(weight="bold")).grid(
                row=0, column=i, padx=5, pady=5, sticky="ew")
        
        # Исправление: правильное обращение к данным школ
        if hasattr(self, 'schools_data') and self.schools_data:
            schools = self.schools_data[0]["schools"][self.school_type.get()]
            for row, school in enumerate(schools, 1):
                # Название школы
                ctk.CTkLabel(self.schools_table_frame, text=school['name']).grid(
                    row=row, column=0, padx=5, pady=5, sticky="w")
                
                # Поля для ввода количества детей
                # Исправление: правильное имя переменной и начальное значение
                school_var = ctk.StringVar(value=str(school.get('child_count', 0)))
                
                school_entry = ctk.CTkEntry(self.schools_table_frame, textvariable=school_var, width=80)
                school_entry.grid(row=row, column=1, padx=5, pady=5)
                
                # Исправление: правильное имя метода и передача параметров
                school_entry.bind('<KeyRelease>', 
                    lambda event, s=school, var=school_var: self.set_child_count(s, var.get()))
                
            # Исправление: настройка колонок после создания виджетов
            self.schools_table_frame.grid_columnconfigure(0, weight=1)
            self.schools_table_frame.grid_columnconfigure(1, weight=0)

    def load_data(self):
        # Загрузка значений из файла
        try:
            values_file_path = self.parent_dir.parent / 'common_values.txt'  # Исправлен путь
            
            if values_file_path.exists():
                with open(values_file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip()
                            value = value.strip()
                                
                            if key == "Стоимость дня":
                                self.common_values["cost_eat"].set(float(value))
                            elif key == "Кол-во дней":
                                self.common_values["day_count"].set(int(value))
                            elif key == "Дата":
                                self.common_values["date"].set(value)
                            elif key == "Дата заключения договора":
                                self.common_values["date_conclusion"].set(value)
                            elif key == "Год":
                                self.common_values["year"].set(value)

            # Загрузка конфига школ
            config_file = self.parent_dir / "data" / "config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.schools_data = json.load(f)
                
                self.update_schools_display()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки данных: {str(e)}")

    def load_values(self):
        """Загрузка значений из файла"""
        self.load_data()
        messagebox.showinfo("Успех", "Данные загружены!")

    def save_values(self):
        """Сохранение значений в файл"""
        try:
            # Сохранение common_values
            values_file = self.parent_dir.parent / 'common_values.txt'
            with open(values_file, 'w', encoding='utf-8') as f:
                f.write(f"Стоимость дня: {self.common_values['cost_eat'].get()}\n")
                f.write(f"Кол-во дней: {self.common_values['day_count'].get()}\n")
                f.write(f"Дата: {self.common_values['date'].get()}\n")
                f.write(f"Дата заключения договора: {self.common_values['date_conclusion'].get()}\n")
                f.write(f"Год: {self.common_values['year'].get()}\n")
            
            messagebox.showinfo("Успех", "Данные сохранены!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")

    # Исправление: правильное имя метода и параметров
    def set_child_count(self, school, value):
        """Установка количества детей для школы"""
        try:
            school["child_count"] = int(value) if value else 0
        except ValueError:
            # Если введено не число, игнорируем
            pass

    def currency_word(self, rubles, kopecks):
        # Исправление: обработка нулевых значений
        if rubles == 0:
            declension_ruble_word = "рублей"
        elif rubles % 10 == 1 and rubles % 100 != 11:
            declension_ruble_word = "рубль"
        elif 2 <= rubles % 10 <= 4 and (rubles % 100 < 10 or rubles % 100 >= 20):
            declension_ruble_word = "рубля"
        else:
            declension_ruble_word = "рублей"

        if kopecks == 0:
            declension_kopecks_word = "копеек"
        elif kopecks % 10 == 1 and kopecks % 100 != 11:
            declension_kopecks_word = "копейка"
        elif 2 <= kopecks % 10 <= 4 and (kopecks % 100 < 10 or kopecks % 100 >= 20):
            declension_kopecks_word = "копейки"
        else:
            declension_kopecks_word = "копеек"

        return declension_ruble_word, declension_kopecks_word

    def number_to_words(self, value):
        try:
            parts = str(value).split('.')
            rubles = int(parts[0])
            
            if len(parts) > 1:
                kopecks_str = parts[1]
                if len(kopecks_str) == 1:
                    kopecks_str += '0'
                kopecks = int(kopecks_str)
            else:
                kopecks = 0 
        
            declension_ruble_word, declension_kopecks_word = self.currency_word(rubles, kopecks)

            rubles_words = num2words(rubles, lang='ru') + f" {declension_ruble_word}"
            kopecks_formatted = f"{kopecks:02d}"
            kopecks_words = f" {kopecks_formatted} {declension_kopecks_word}"
            
            return rubles_words + kopecks_words
        except Exception as e:
            return f"Ошибка преобразования числа: {str(e)}"

    def generate_contracts(self):  # Исправлено имя метода
        """Генерация договоров"""
        try:
            self.log_text.delete("1.0", "end")
            self.log_text.insert("end", "Начало генерации договоров...\n")
            self.update()

            # Проверка заполнения общих параметров
            if not all([self.common_values[key].get() for key in self.common_values]):
                messagebox.showwarning("Внимание", "Заполните все общие параметры!")
                return

            # Определение типа школы для названия папки
            self.type_name_ru = "Город" if self.school_type.get() == "town" else "Район"
            
            current_time = datetime.now().strftime("%Y.%m.%d (%H:%M)")
            new_output_folder_name = f"{self.type_name_ru} договоры от {current_time}"
            folder_output = self.output_dir / new_output_folder_name
            
            # Создание папки с проверкой существования
            if folder_output.exists():
                result = messagebox.askyesno("Папка существует", 
                                           "Папка уже существует. Перезаписать содержимое?")
                if not result:
                    self.log_text.insert("end", "Генерация отменена пользователем\n")
                    return
            else:
                folder_output.mkdir(parents=True, exist_ok=True)

            # Проверка наличия данных о школах
            if not hasattr(self, 'schools_data') or not self.schools_data:
                messagebox.showerror("Ошибка", "Данные о школах не загружены!")
                return

            schools = self.schools_data[0]["schools"][self.school_type.get()]
            total_schools = len(schools)
            
            self.progress_bar.set(0)
            
            successful_count = 0
            for i, school in enumerate(schools):
                try:
                    self.log_text.insert("end", f"Обработка {school['name']}...\n")
                    self.log_text.see("end")
                    self.update()
                    
                    # Получение значений из common_values
                    cost_eat = self.common_values["cost_eat"].get()
                    day_count = self.common_values["day_count"].get()
                    
                    template_path = self.templates_dir / "contracts" / "contract_template.docx"
                    
                    if not template_path.exists():
                        self.log_text.insert("end", f"Ошибка: шаблон не найден {template_path}\n")
                        continue

                    # Загрузка шаблона
                    doc = DocxTemplate(template_path)

                    # Расчет стоимости
                    cost_eat_decimal = Decimal(str(cost_eat))
                    day_count_decimal = Decimal(str(day_count))
                    child_count_decimal = Decimal(str(school.get('child_count', 0)))

                    count_money = cost_eat_decimal * day_count_decimal * child_count_decimal
                    count_money = count_money.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    
                    decoding_number_words = self.number_to_words(count_money) 

                    # Название для договора
                    name_doc = f"{school['name']} договор от {current_time}.docx"

                    # Формирование информации о классификаторах
                    classification_info_text = ""
                    if 'bank_account_info' in school and school['bank_account_info']:
                        classification_info_text = "\n".join(
                            f"{info['name']}: {info['value']}"
                            for info in school['bank_account_info'][0].get('classification_info', [])
                        )
                
                    # Создание контекста для подстановки
                    context = {
                        'child_count': school.get('child_count', 0), 
                        'day_count': day_count,
                        'cost_eat': locale.format_string('%.2f', cost_eat, grouping=True),
                        'count_money': locale.format_string('%.2f', float(count_money), grouping=True),
                        'decoding_number_words': decoding_number_words, 
                        'date': self.common_values["date"].get(),
                        'date_conclusion': self.common_values["date_conclusion"].get(),
                        'year': self.common_values["year"].get(),
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
                    output_path = folder_output / name_doc
                    doc.save(output_path)
                    
                    successful_count += 1
                    self.log_text.insert("end", f"Успешно: {name_doc}\n")
                    
                except Exception as e:
                    self.log_text.insert("end", f"Ошибка при обработке {school['name']}: {str(e)}\n")
                
                # Обновление прогресс-бара
                progress = (i + 1) / total_schools
                self.progress_bar.set(progress)
                self.update()

            self.log_text.insert("end", f"\nГенерация завершена! Успешно обработано: {successful_count}/{total_schools} школ\n")
            messagebox.showinfo("Успех", f"Договоры успешно сгенерированы! Обработано {successful_count}/{total_schools} школ")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации: {str(e)}")
            self.log_text.insert("end", f"Критическая ошибка: {str(e)}\n")


if __name__ == "__main__":
    app = ContractAuto_App()
    app.mainloop()