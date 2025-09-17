from docxtpl import DocxTemplate
import sys
import os 
from num2words import num2words
from datetime import datetime
import json
from pathlib import Path

# найти файл- открыть файл - прочитать файл - прочитать строки и разделить их до ":" и после
# Чистка кода 
# сделать перевод district and town для названий папок
# сделать шаблоны школ города
# перезапись старых решений с запросом этого у юзера
# try except 
# СКЛОНЕНИЯ ДЛЯ РУБЛЕЙ
# ДАТА В ФУТЕРЕ НЕ СТАВИТСЯ  И ГОД ПЕРЕНОСИТСЯ
# проверить работу с датами ноябрь-декабрь
# сделать русские названия выводных папок
# добавить шаблоны городских школ
# добавить обработчики ошибок
# добавить склонения для денег
# копейки от 6
# точка в файле меняется на запятую
# добавить возможность очистки папки вывода от старых решений
# шаблоны для школ
# чтобы прога была вроде exe и можно было бы скачать с гитхаба
# шаблоны по октябряь - ноябрь и ноябрь - декабрь однотипные, поэтому можно делать по единым шаблонам в одной папке, где меняется только даты 
# возможно, добавить ui
# добавить файл с зависимостями
# config в json


#variables / find directions to files
script_dir = os.path.dirname(os.path.abspath(__file__))
script_dir = Path(__file__).parent


parent_dir = script_dir.parent

templates_dir = parent_dir / "templates"
output_dir = parent_dir.parent / "schools_output"

#other var
school_type = ""

    
#TEST PART
    #создавать папку в school_output в зависимости от это район или город,
    #То есть f"{administrative_structure_name} договоры {current_time}"(Район договор 12-09-2025) 
day_count = 40
cost_eat = 73.51 
date = "сентября 2025"
date_conclusion = "с 1 сентября 2025 года по 31 октября 2025 года"


school_type_answer = int(input("район или город? (1/2): "))
if school_type_answer == 1:
    school_type = "district"
else:
    school_type = "town"


#вынести в txt
#day_count = int(input("кол-во дней: "))
#cost_eat = float(input("стоимость дня: "))
#date = str(input("дата: "))

#concl_date_one_part = str(input("С какого числа и года? (в род падеже)"))
#concl_date_two_part = str(input("По какое число и год?(в род падеже)"))
#date_conclusion =  f"с {concl_date_one_part} по {concl_date_two_part}"


#open json
folder_config_dir = parent_dir / "data" / "config.json"

with open(folder_config_dir) as file:
    schools_data = json.load(file)


#задаем кол-во детей
i=0
for schools in schools_data[0]["schools"][school_type]:
       
    print(i)
    get_childs_count_from_user = int(input( f"{schools['name']}: "))
    schools["child_count"] = get_childs_count_from_user
    i=i+1
    
#мб в другой файл
def number_to_words(value):
    #должны быть сделаны окончания и проверка на полное число или же отсутсвие копеек другими словами, также прибавленеи нуля в конце, если копейка меньше 10
    
    parts = str(value).split('.')
    rubles = int(parts[0])
    kopecks = int(parts[1]) if len(parts) > 1 else 0
    
    rubles_words = num2words(rubles, lang='ru') + ' рублей'
    kopecks_words = f" {kopecks} копеек"
    
    return rubles_words + kopecks_words
    
    

#date
current_time = datetime.now().strftime("%Y-%m-%d")

#create a new folder in school_output
new_output_folder_name = f"{school_type} договоры от {current_time}"
folder_output = output_dir / new_output_folder_name
folder_output.mkdir(parents=True, exist_ok=True)
    
i=0
for school in schools_data[0]["schools"][school_type]:

    print(f"id: {school['id']}")

    template_path = templates_dir / school_type / f"{school['name']}.docx"

    # Загрузка шаблона
    doc = DocxTemplate(template_path)

    count_money = cost_eat * day_count * school['child_count']
    decoding_number_words = number_to_words(count_money) 

        
    name_doc = f"{school['name']} договор от {current_time}"

        
    # Создание контекста для подстановки (переменные в документе)
    context = {
            
        'child_count': school["child_count"], 
        'day_count': day_count,
        'cost_eat': cost_eat, 
        'count_money': count_money,
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
