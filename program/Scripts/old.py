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

# разделить на функцию старта и чтения и всего такого и основной функции
# сделать сохранения  в конфиг child_count 
# добавить возможность добалвения в конфиг пользователем для каждой школы()
# сделать чтобы у пользователя запрашивалось по каждой школе про обучающихся с 1-5, c 5-11 классы то есть по классам чтобы пользователь вводил а потом все это суммировалось. в итоге вместо child_count в конфиге будут по классам в каждой школе
# в будущем добавить возможность добавлять школы из интерфейса
# добавить комментарии
# new templates -> change config -> classification_info func -> OOP -> UI -> ADDITIONAL contr FUNC
# допники добавить(создание отдельных договоров)
# добавить обработчики ошибок
# добавить проверку try except 
# добавить возможность очистки папки вывода от старых решений
# чтобы прога была вроде exe и можно было бы скачать с гитхаба
# возможно, добавить ui
# добавить файл с зависимостями

class ContractAuto_App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Настройка основного окна
        self.title("Авто Договор")
        self.geometry("600x400")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        #variables / find directions to files
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.script_dir = Path(__file__).parent
        self.parent_dir = self.script_dir.parent

        self.templates_dir = self.parent_dir / "templates"
        self.output_dir = self.parent_dir.parent / "schools_output"

        #other var
        self.school_type = ""
        self.type_name_ru = ""

        self.common_values = {
            "cost_eat": ctk.DoubleVar(value=0.0),
            "day_count": ctk.IntVar(value=0),
            "date": ctk.StringVar(value=""),
            "date_conclusion": ctk.StringVar(value=""),
            "year": ctk.StringVar(value="")
        }

        # Устанавливаем русскую локаль для корректного форматирования чисел
        locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

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
            entry = ctk.CTkEntry(tab, textvariable = self.common_values[key])
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


    # страница генерации договора
    def setup_generation_tab(self):
        tab = self.tabview.tab("Генерация")
        tab.grid_columnconfigure(0, weight=1)
        
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
        
    # обновить отображение школ в зависимости от района или города
    def update_schools_display(self):
        # Очистка предыдущего отображения
        for widget in self.schools_table_frame.winfo_children():
            widget.destroy()
      
        # Заголовки таблицы (без классов)
        headers = ["Школа", "Кол-во детей"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(self.schools_table_frame, text=header, font=ctk.CTkFont(weight="bold")).grid(
                row=0, column=i, padx=5, pady=5)
        
        # Данные школ
        # получаем данные из конфига
        schools = self.schools_data[0]["schools"][self.school_type.get()]
        for row, school in enumerate(schools, 1):
            # Название школы
            ctk.CTkLabel(self.schools_table_frame, text=school['name']).grid(
                row=row, column=0, padx=5, pady=5)
            
            # Поля для ввода количества детей
            school_var = ctk.IntVar(value=school.get('primary_count', 0))
            
            school_entry = ctk.CTkEntry(self.schools_table_frame, textvariable=school_var, width=80)
            school_entry.grid(row=row, column=1, padx=5, pady=5)
            # Передаем школу и значение через lambda
            school_entry.bind('<KeyRelease>', 
                lambda event, s=school, var=school_var: self.Set_childCount(s, var.get()))
            
            
    def load_data(self):
        #read values from txt file
        try:
            values_file_path = self.parent_dir.parent / 'common_values.txt'
            
            # Проверка существования файла
            if not os.path.exists(values_file_path):
                print(f"Файл {values_file_path} не найден!")
            else:

                # Открытие файла
                with open(values_file_path, 'r', encoding='utf-8') as file:
                
                    # Чтение построчно
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

    

    # сделать  чтобы значение задавалось из введенных  в строку до этого в ui
    def Set_ChildCount(self,value):
        #задаем кол-во детей
        i=0
        for schools in self.schools_data[0]["schools"][self.school_type]:
            
            get_childs_count_from_user = int(input( f"{schools['name']}: "))
            schools["child_count"] = get_childs_count_from_user
            i=i+1
    

    def Currency_Word(self, rubles,kopecks):
        # Проверка для рублей
        if rubles % 10 == 1 and rubles % 100 != 11:
            declension_ruble_word = "рубль"
        elif 2 <= rubles % 10 <= 4 and (rubles % 100 < 10 or rubles % 100 >= 20):
            declension_ruble_word = "рубля"
        else:
            declension_ruble_word = "рублей"

        # Проверка для копеек
        if kopecks % 10 == 1 and kopecks % 100 != 11:
            declension_kopecks_word = "копейка"
        elif 2 <= kopecks % 10 <= 4 and (kopecks % 100 < 10 or kopecks % 100 >= 20):
            declension_kopecks_word = "копейки"
        else:
            declension_kopecks_word = "копеек"

        return declension_ruble_word, declension_kopecks_word


    def number_to_words(self, value):
        
        parts = str(value).split('.')
        rubles = int(parts[0])
        
        # Обрабатываем копейки, добавляем ведущий ноль если нужно
        if len(parts) > 1:
            kopecks_str = parts[1]
            # Добавляем ведущий ноль, если копеек меньше 10
            if len(kopecks_str) == 1:
                kopecks_str += '0'
            kopecks = int(kopecks_str)
        else:
            kopecks = 0 
    
        declension_ruble_word, declension_kopecks_word = self.Currency_Word(rubles,kopecks)

        rubles_words = num2words(rubles, lang='ru') + f" {declension_ruble_word}"
        # Форматируем копейки (добавляем ведущий ноль при необходимости)
        kopecks_formatted = f"{kopecks:02d}"  # Форматируем к двузначному числу
        kopecks_words = f" {kopecks_formatted} {declension_kopecks_word}"
        
        return rubles_words + kopecks_words
    

    def generate_contract(self):
        """Генерация договоров"""
        try:
            self.log_text.delete("1.0", "end")
            self.log_text.insert("end", "Начало генерации договоров...\n")

            #date (year month day hour minutes)
            current_time = datetime.now().strftime("%Y.%m.%d ( %H:%M )")

            #create a new folder in school_output(dont work now)
            new_output_folder_name = f"{self.type_name_ru} договоры от {current_time}"
            folder_output = self.output_dir / new_output_folder_name
            try:
                folder_output.mkdir(parents=True, exist_ok=True) #поменять exist на True чтобы обрабатывать исключения при создании уже существующей папки
            except:
                #test part
                try:
                    rewrite_dir = str(input("Папка уже существует. Старая будет перезаписана? (да / нет) ")).strip().lower()
                    if rewrite_dir == "да":
                        pass
                    if rewrite_dir == "нет":
                        #добавляем к названию папки (1)
                        print("Программа завершена без создания директории")
                        sys.exit()
                    else:
                        print("Кажется, что-то пошло не так. Попробуйте еще раз")
                except:
                    print("Кажется, что-то пошло не так. Попробуйте еще раз")


            i=0
            for school in self.schools_data[0]["schools"][self.school_type]:

                print(f"id: {school['id']}")

                template_path = self.templates_dir / "contracts" / "contract_template.docx"

                # Загрузка шаблона
                doc = DocxTemplate(template_path)

                #считаем
                #here using decimal for accurate calculations
                cost_eat_decimal = Decimal(str(self.cost_eat))
                day_count_decimal = Decimal(str(self.day_count))
                child_count_decimal = Decimal(str(school['child_count']))

                count_money = cost_eat_decimal * day_count_decimal * child_count_decimal
                # Округляем до 2 знаков после запятой
                count_money = count_money.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                
                # Преобразование подсчитанного значения в текст
                decoding_number_words = self.number_to_words(count_money) 

                #название для договора
                name_doc = f"{school['name']} договор от {current_time}"

                # отображение всех классификаторов деятельности школ из конфига в инфе счета в документе
                classification_info_text = "\n".join(
                        f"{info['name']}: {info['value']}"
                        for info in school['bank_account_info'][0]['classification_info']
                    )
                
                #variables context
                year = self.year
                contract_number = school['contract_number']
                school_full_name = school['school_full_name'] 
                school_short_name = school['school_short_name'] 
                director_full_name = school['director_full_name'] 
                director_short_name = school['director_short_name']
                postal_code = school['postal_code']
                full_location_school = school['full_location_school']
                personal_account = school['bank_account_info'][0]['personal_account']
                INN = school['bank_account_info'][0]['INN']
                classification_info = classification_info_text

                # Создание контекста для подстановки (переменные в документе)
                context = {
                        
                    'child_count': school["child_count"], 
                    'day_count': self.day_count,
                    'cost_eat': locale.format_string('%.2f', self.cost_eat, grouping=True), #всегда есть 00 после целого числа то есть всегда float
                    'count_money': locale.format_string('%.2f', float(count_money), grouping=True), #всегда есть 00 после целого числа то есть всегда float
                    'decoding_number_words': decoding_number_words, 
                    'date': self.date,
                    'date_conclusion': self.date_conclusion,
                    
                    'year': year,
                    'contract_number': contract_number,
                    'school_full_name': school_full_name,
                    'school_short_name': school_short_name,
                    'director_full_name': director_full_name,
                    'director_short_name': director_short_name,
                    'postal_code':  postal_code,
                    'full_location_school': full_location_school,
                    'personal_account': personal_account,
                    'INN': INN,
                    'classification_info': classification_info

                    }

                i=i+1
                    # Подстановка значений
                doc.render(context)

                output_path = folder_output / f"{name_doc}.docx"
                    # Сохранение результата
                doc.save(output_path)

                
                if not all([self.common_values[key].get() for key in self.common_values]):
                    messagebox.showwarning("Внимание", "Заполните все общие параметры!")
                    return

                self.log_text.insert("end", "Генерация завершена успешно!\n")
                messagebox.showinfo("Успех", "Договоры успешно сгенерированы!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации: {str(e)}")


if __name__ == "__main__":
    app = ContractAuto_App()
    app.mainloop()