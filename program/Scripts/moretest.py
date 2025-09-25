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

# Настройка внешнего вида
ctk.set_appearance_mode("System")  # Режим: "Light", "Dark" или "System"
ctk.set_default_color_theme("green")  # Темы: "blue", "green", "dark-blue"

# добавить возможность добалвения в конфиг пользователем для каждой школы()
# сделать чтобы у пользователя запрашивалось по каждой школе про обучающихся с 1-5, c 5-11 классы то есть по классам чтобы пользователь вводил а потом все это суммировалось. в итоге вместо child_count в конфиге будут по классам в каждой школе
# в будущем добавить возможность добавлять школы из интерфейса
# добавить комментарии
# new templates -> change config -> classification_info func -> OOP -> UI -> ADDITIONAL contr FUNC
# переход на класс
# дата склон
# допники добавить(создание отдельных договоров)
# добавить обработчики ошибок
# добавить склонения для денег
# точка в файле меняется на запятую
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
        
        # Создание виджетов
        self.create_widgets()

        #variables / find directions to files
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.script_dir = Path(__file__).parent
        self.parent_dir = self.script_dir.parent

        self.templates_dir = self.parent_dir / "templates"
        self.output_dir = self.parent_dir.parent / "schools_output"

        #other var
        self.school_type = ""
        self.type_name_ru = ""

        self.day_count = 0
        self.cost_eat = 0 
        self.date = ""
        self.date_conclusion = ""
        self.year = ""

        # Устанавливаем русскую локаль для корректного форматирования чисел
        locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

        self.read_values()
        self.read_json()
        self.school_type_answer()
        self.Set_ChildCount()
        self.contract_fill()

    def create_widgets(self):
        # Метка
        self.label = ctk.CTkLabel(self, 
                                 text="Добро пожаловать в CustomTkinter!",
                                 font=ctk.CTkFont(size=16, weight="bold"))
        self.label.pack(pady=20)
        
        # Поле ввода
        self.entry = ctk.CTkEntry(self, 
                                 placeholder_text="Введите текст здесь",
                                 width=300)
        self.entry.pack(pady=10)
        
        # Кнопка
        self.button = ctk.CTkButton(self, 
                                   text="Нажми меня",
                                   command=self.button_callback)
        self.button.pack(pady=10)
        
        # Переключатель тем
        self.theme_switch = ctk.CTkSwitch(self,
                                         text="Темная тема",
                                         command=self.toggle_theme)
        self.theme_switch.pack(pady=20)
        
        # Выпадающий список
        self.combobox = ctk.CTkComboBox(self,
                                       values=["Вариант 1", "Вариант 2", "Вариант 3"])
        self.combobox.pack(pady=10)
        
        # Ползунок
        self.slider = ctk.CTkSlider(self,
                                   from_=0,
                                   to=100,
                                   number_of_steps=10)
        self.slider.pack(pady=10)

    def button_callback(self):
        text = self.entry.get()
        messagebox.showinfo("Уведомление", f"Вы ввели: {text}")
    
    def toggle_theme(self):
        if self.theme_switch.get():
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")



    def read_values(self):
        #read values from txt file
        values_file_path = self.parent_dir.parent / 'common_values.txt'
        
        # Проверка существования файла
        if not os.path.exists(values_file_path):
            print(f"Файл {values_file_path} не найден!")
        else:

            # Открытие файла
            with open(values_file_path, 'r', encoding='utf-8') as file:
            
                # Чтение построчно
                for line in file:

                    line = line.strip()  # Удаляем пробелы и переносы строк
            
                    # Разделяем строку по двоеточию и проверяем на существование двоеточия
                    if ':' in line:
                
                        part_after_colon = line.split(':', 1)[1].strip()
                        part_before_colon = line.split(':',1)[0].strip()
                
                        if part_before_colon == "Стоимость дня":
                            self.cost_eat = float(part_after_colon)
                        if part_before_colon == "Кол-во дней":
                            self.day_count = int(part_after_colon)
                        if part_before_colon == "Дата":
                            self.date = part_after_colon
                        if part_before_colon == "Дата заключения договора":
                            self.date_conclusion = part_after_colon
                        if part_before_colon == "Год":
                            self.year = part_after_colon

                    else:

                        # Обработка строк без двоеточия
                        print(f"Строка без двоеточия: {line}")


    def read_json(self):
        #open json
        folder_config_dir = self.parent_dir / "data" / "config.json"

        with open(folder_config_dir) as file:
            self.schools_data = json.load(file)


    def school_type_answer(self):
        #answer for user about school type
        school_type_answer = int(input("район или город? (1/2): "))
        if school_type_answer == 1:
            self.school_type = "district"
            self.type_name_ru = "Район"
        else:
            self.school_type = "town"
            self.type_name_ru = "Город"


    def Set_ChildCount(self):
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
        #должны быть сделаны окончания и проверка на полное число или же отсутсвие копеек другими словами, также прибавленеи нуля в конце, если копейка меньше 10
        #копейки сбиваются число и получается что коп и числ меняются местами т е коп 5
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
    

    def contract_fill(self):
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

            print(f"{name_doc} успешно создан!")


if __name__ == "__main__":
    app = ContractAuto_App()
    app.mainloop()