import json
import os
from pathlib import Path
from decimal import Decimal

script_dir = Path(__file__).parent
parent_dir = script_dir.parent

odir = parent_dir / "data" / "config.json"
folder = "/config.json"


with open(odir) as file:
    schools_data = json.load(file)

date_conclusion=""
values_file_path = parent_dir.parent / 'common_values.txt'

d=Decimal(float(73.50))
formatted_price = format(d, '.2f')
def format_number(num):
    return f"{num:.2f}".rstrip('0').rstrip('.') if num % 1 else int(num)
print(formatted_price)
# Проверка существования файла
if not os.path.exists(values_file_path):
    print(f"Файл {values_file_path} не найден!")
else:
    # Открытие файла
    with open(values_file_path, 'r', encoding='utf-8') as file:
        # Чтение построчно
        for line in file:
            line = line.strip()  # Удаляем пробелы и переносы строк
            
            # Разделяем строку по двоеточию
            if ':' in line:
                
                part_after_colon = line.split(':', 1)[1].strip()
                part_before_colon = line.split(':',1)[0].strip()
                #print(part_after_colon)
                #print(part_before_colon)
                if part_before_colon == "Дата заключения договора":
                    date_conclusion = part_after_colon
                print(date_conclusion)
            else:
                # Обработка строк без двоеточия
                print(f"Строка без двоеточия: {line}")

school_type='town'
#3#3#@#33№№№def bi(integ):
    
    #return ready

#print(schools_data[0])

i=0
print(schools_data[0]["schools"][school_type][0]['type'])#['bank_account_info'][0]['personal_account'])
for school in schools_data[0]["schools"][school_type]:
        #personal_account = school['bank_account_info'][0]['personal_account'] #['bank_account_info']['personal_account']
        #print(personal_account)
        #print(school['bank_account_info'][0]['personal_account'])
        #print(f"ключ: {имя школы}")
        #print("name:", f"{school['schools'][school_type][i]['name']}.docx")
        print(school['name'])
        
        #count_money = school['schools'][school_type][i]['child_count']
        #lines = []
        
            
            #line = f"{info['name']}: {info['value']}"
            #lines.append(line)
        #print(lines)
        classification_info_text = "\n".join(
            f"{info['name']}: {info['value']}"
            for info in school['bank_account_info'][0]['classification_info']
        )
        print(result_text)
        
       # name_doc = f"{school['schools'][school_type][i]['name']} договор от 12.09"
      #  print(count_money)
       # print(name_doc)
        i=i+1 


