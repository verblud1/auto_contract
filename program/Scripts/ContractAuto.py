from docxtpl import DocxTemplate
import sys
import os 
from num2words import num2words
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from district_schools_config import schools_list

# не происходит вызов из словаря школы 
# добавить обработчики ошибок
# добавить склонения для денег
# копейки от 6
# точка в файле меняется на запятую
# добавить возможность очистки папки вывода от старых решений
# шаблоны для школ
#конфиги и чтение из них 
#txt значения либо ввод в консоли
#чтобы прога была вроде exe и можно было бы скачать с гитхаба
#шаблоны по октябряь - ноябрь и ноябрь - декабрь однотипные, поэтому можно делать по единым шаблонам в одной папке, где меняется только даты 
# возможно, добавить ui
# добавить файл с зависимостями
#config в json

class AutoContract(self):

    def __init__(self):
        
        #variables
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        self.output_folder = "schools_output"
        self.templates_folder = "templates"

        self.output_dir = os.path.join(self.script_dir, self.output_folder) 
        self.templates_dir = os.path.join(self.script_dir, self.templates_folder) 
        self.school_list_child = schools_list

        #scripts queue
        


    #получить названия ключей, потом в них вывести значения ключа name в input,
    # а потом записать введенное в input в значение ключа child_count  
    
    #TEST PART
    #создавать папку в school_output в зависимости от это район или город,
    #То есть f"{administrative_structure_name} договоры {current_time}"(Район договор 12-09-2025) 
    day_count = 40
    cost_eat = 73.51 
    date = "сентября 2025"
    date_conclusion = "с 1 сентября 2025 года по 31 октября 2025 года"

    #len example for i in range(len(school_name_list)):    
    
    i=0
    for key in self.school_list_childs: 
        print(i)
        print(key)
        get_childs_count = int(input(f"{school_name_list[i]}: "))
        school_list_childs[key] = get_childs_count
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
    
    def document_fill(self):
        i=0
        for key in school_list_childs:
            print(f"ключ: {key}")
            template_path =  os.path.join(templates_dir, f"{key}.docx")
            # Загрузка шаблона
            doc = DocxTemplate(template_path)

            count_money = cost_eat * day_count * school_list_childs[key]
            decoding_number_words = number_to_words(count_money) 

            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
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

            output_path = os.path.join(output_dir,f"{name_doc}.docx")
            # Сохранение результата
            doc.save(output_path)

            print(f"{name_doc} успешно создан!")

if __name__ == "__main__":
    main = AutoContract()
    exit()