from docxtpl import DocxTemplate
import sys
import os 
from num2words import num2words
from datetime import datetime
import json
from pathlib import Path

#переход с os на pathlib
# добавить шаблоны городских школ
# добавить обработчики ошибок
# добавить склонения для денег
# копейки от 6
# точка в файле меняется на запятую
# добавить возможность очистки папки вывода от старых решений
# шаблоны для школ
#конфиги и чтение из них 
#чтобы прога была вроде exe и можно было бы скачать с гитхаба
#шаблоны по октябряь - ноябрь и ноябрь - декабрь однотипные, поэтому можно делать по единым шаблонам в одной папке, где меняется только даты 
# возможно, добавить ui
# добавить файл с зависимостями
#config в json

#variables / find directions to files
script_dir = os.path.dirname(os.path.abspath(__file__))

script_dir = Path(__file__).parent
output_dir = script_dir / "schools_output"
templates_dir = script_dir / "templates"

school_list_child = schools_list

#other var
school_type = ""

#open json
parent_dir = script_dir.parent

folder_config_dir = parent_dir / "data" / "config.json"

with open(folder_config_dir) as file:
    schools_data = json.load(file)
    
#scripts queue
        


    #получить названия ключей, потом в них вывести значения ключа name в input,
    # а потом записать введенное в input в значение ключа child_count  
    
    #TEST PART
    #создавать папку в school_output в зависимости от это район или город,
    #То есть f"{administrative_structure_name} договоры {current_time}"(Район договор 12-09-2025) 
#day_count = 40
#cost_eat = 73.51 
#date = "сентября 2025"
#date_conclusion = "с 1 сентября 2025 года по 31 октября 2025 года"

    #len example for i in range(len(school_name_list)):    
school_type_answer = int("район или город? (1/2): ")
if school_type_answer == 1:
    school_type = "district"
else:
    school_type = "town"
        
#мб вынести в txt
day_count = int(input("кол-во дней: "))
cost_eat = int(input("стоимость дня: "))
date = str(input("дата: "))

concl_date_one_part = str(input("С какого числа и года? (в род падеже)"))
concl_date_two_part = str(input("По какое число и год?(в род падеже)"))
date_conclusion =  f"с {concl_date_one_part} по {concl_date_two_part}"

#вывод циклом из config.json 

i=0
for schools in schools_data:
       
    #print(i)
    #print(key)
    get_childs_count_from_user = int(input(f"{schools["schools"][school_type][i]["name"]}: "))
    schools["schools"][school_type][i]["child_count"] = get_childs_count_from_user
    i=i+1
    
    #мб в другой файл

def number_to_words(self,value):
    #должны быть сделаны окончания и проверка на полное число или же отсутсвие копеек другими словами, также прибавленеи нуля в конце, если копейка меньше 10
    
    parts = str(value).split('.')
    rubles = int(parts[0])
    kopecks = int(parts[1]) if len(parts) > 1 else 0
    
    rubles_words = num2words(rubles, lang='ru') + ' рублей'
    kopecks_words = f" {kopecks} копеек"
    
    return rubles_words + kopecks_words
    
def document_fill():
    
    #date
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    #create a new folder in school_output
    new_output_folder_name = "{тип адм структуры} договоры от {дата}"
    folder_output = output_dir / new_output_folder_name
    folder_output.mkdir(parents=True, exist_ok=True)
    
    i=0
    for key in school_list_childs:
        print(f"ключ: {имя школы}")
        template_path = templates_dir / f"{имя школы}.docx"

        # Загрузка шаблона
        doc = DocxTemplate(template_path)

        count_money = cost_eat * day_count * school_list_childs[key]
        decoding_number_words = number_to_words(count_money) 

        
        name_doc = f'{school_name_list[i]} договор от {current_time}'

        #main
        # Создание контекста для подстановки (переменные в документе)
        context = {
            
            'child_count': school_list_childs[key], #ост
            'day_count': day_count,
            'cost_eat': cost_eat, 
            'count_money': count_money,# ост
            'decoding_number_words': decoding_number_words, #ост
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
