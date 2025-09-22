from docxtpl import DocxTemplate
from num2words import num2words
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import json
import sys
import os 

# дата склон
# добавить обработчики ошибок
# добавить склонения для денег
# точка в файле меняется на запятую
# добавить проверку try except 
# добавить возможность очистки папки вывода от старых решений
# чтобы прога была вроде exe и можно было бы скачать с гитхаба
# возможно, добавить ui
# добавить файл с зависимостями

#variables / find directions to files
script_dir = os.path.dirname(os.path.abspath(__file__))
script_dir = Path(__file__).parent
parent_dir = script_dir.parent

templates_dir = parent_dir / "templates"
output_dir = parent_dir.parent / "schools_output"

#other var
school_type = ""
type_name_ru = ""

day_count = 0
cost_eat = 0 
date = ""
date_conclusion = ""

#read values from txt file
values_file_path = parent_dir.parent / 'common_values.txt'
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
                    cost_eat = float(part_after_colon)
                if part_before_colon == "Кол-во дней":
                    day_count = int(part_after_colon)
                if part_before_colon == "Дата":
                    date = part_after_colon
                if part_before_colon == "Дата заключения договора":
                    date_conclusion = part_after_colon

            else:
                # Обработка строк без двоеточия
                print(f"Строка без двоеточия: {line}")


#answer for user about school type
school_type_answer = int(input("район или город? (1/2): "))
if school_type_answer == 1:
    school_type = "district"
    type_name_ru = "Район"
else:
    school_type = "town"
    type_name_ru = "Город"


#open json
folder_config_dir = parent_dir / "data" / "config.json"

with open(folder_config_dir) as file:
    schools_data = json.load(file)


#задаем кол-во детей
i=0
for schools in schools_data[0]["schools"][school_type]:
       
    get_childs_count_from_user = int(input( f"{schools['name']}: "))
    schools["child_count"] = get_childs_count_from_user
    i=i+1
    
def Currency_Word(rubles,kopecks):
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

def number_to_words(value):
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
 
    declension_ruble_word, declension_kopecks_word = Currency_Word(rubles,kopecks)

    rubles_words = num2words(rubles, lang='ru') + f" {declension_ruble_word}"
    # Форматируем копейки (добавляем ведущий ноль при необходимости)
    kopecks_formatted = f"{kopecks:02d}"  # Форматируем к двузначному числу
    kopecks_words = f" {kopecks_formatted} {declension_kopecks_word}"
    
    return rubles_words + kopecks_words
    


#date (year month day hour minutes)
current_time = datetime.now().strftime("%Y.%m.%d ( %H:%M )")

#create a new folder in school_output(dont work now)
new_output_folder_name = f"{type_name_ru} договоры от {current_time}"
folder_output = output_dir / new_output_folder_name
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
for school in schools_data[0]["schools"][school_type]:

    print(f"id: {school['id']}")

    template_path = templates_dir / school_type / f"{school['name']}.docx"

    # Загрузка шаблона
    doc = DocxTemplate(template_path)

    #here using decimal for accurate calculations
    cost_eat_decimal = Decimal(str(cost_eat))
    day_count_decimal = Decimal(str(day_count))
    child_count_decimal = Decimal(str(school['child_count']))

    count_money = cost_eat_decimal * day_count_decimal * child_count_decimal
    # Округляем до 2 знаков после запятой
    count_money = count_money.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    decoding_number_words = number_to_words(count_money) 

        
    name_doc = f"{school['name']} договор от {current_time}"

        
    # Создание контекста для подстановки (переменные в документе)
    context = {
            
        'child_count': school["child_count"], 
        'day_count': day_count,
        'cost_eat': format(cost_eat,'.2f'), #всегда есть 00 после целого числа то есть всегда float
        'count_money': format(count_money,'.2f'), #всегда есть 00 после целого числа то есть всегда float
        'decoding_number_words': decoding_number_words, 
        'date': date,
        'date_conclusion': date_conclusion

        }

    i=i+1
        # Подстановка значений
    doc.render(context)

    output_path = folder_output / f"{name_doc}.docx"
        # Сохранение результата
    doc.save(output_path)

    print(f"{name_doc} успешно создан!")
