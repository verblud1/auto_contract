from docxtpl import DocxTemplate
import os 
from num2words import num2words
from datetime import datetime

# не происходит вызов из словаря школы 
# добавить обработчики ошибок
# добавить склонения для денег
# копейки от 6
# точка в файле меняется на запятую
# добавить возможность очистки папки вывода от старых решений

class AutoContract():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    output_folder = "schools_output"
    templates_folder = "templates"
    
    output_dir = os.path.join(script_dir, output_folder) 
    templates_dir = os.path.join(script_dir, templates_folder) 
    
    #получить названия ключей, потом в них вывести значения ключа name в input,
    # а потом записать введенное в input в значение ключа child_count  
    
    #TEST PART
    #создавать папку в school_output в зависимости от это район или город,
    #То есть f"{administrative_structure_name} договор {current_time}"(Район договор 12-09-2025) 
    day_count = 40
    cost_eat = 73.51 
    date = "сентября 2025"
    date_conclusion = "с 1 сентября 2025 года по 31 октября 2025 года"


    #это будет в текстовом файле и не надо будет юзеру вводить
    #from config
    school_name_list=[
    "академическая",
    "борисовская",
    "горняк",
    "дятловская",
    "есиновичская",
    "зеленогорская",
    "красномайская",
    "солнечная",
    "терелесовская",
    "холохоленская"
    ]
    

    #from config
    #Это будет вынесено в конфиг
    school_list_childs = {
        "akademia": 0,
        "boris": 0,
        "gornyak": 0,
        "dyatlov": 0,
        "yesinovich": 0,
        "zelenogorsk": 0,
        "krasnomay": 0,
        "solnech": 0,
        "tereles": 0,
        "holoh": 0
    }
    
    #нужно сранвить кол-во школ и кол-во списка кол-ва детей
    
    



    
        #for snl in school_name_list:
    #for i in range(len(school_name_list)):    
    
    i=0
    for key in school_list_childs: 
        print(i)
        print(key)
        get_childs_count = int(input(f"{school_name_list[i]}: "))
        school_list_childs[key] = get_childs_count
        i=i+1
    
    # название документа
    #возможно, сделать,чтобы пользователь выбирал между необходимыми ему школами, чтобы подставлялся необходимый шаблон опредленной школы(по причине)
    #сделать папку с шаблонами школ и скрипт по ним проходит и подставляет все указанные пользователем значения для каждого шаблона каждой школы(например сначала пользователь в первый раз указывается только допустим 73 51 и 40 дней то есть неизменяемы нестатические значения во всех доках а потом скрипт скпрашивает про количество школьников в каждой школе и сохраняет в переменную допустим красномайская сколько? ответ есиновичская сколько? ответ и дальше все подсчитвается и создается документ для каждой школы)
    # 
    # Запрос данных у пользователя
    #name_doc = str(input("Введите название документа: ")) #в зависимости от школы
    #child_count = int(input("Введите количество школьников: ")) #разные школы т е изменяемо
    #day_count = int(input("Введите количество дней: ")) #единичный запрос
    #cost_eat = float(input("Введите стоимость питания: ")) единичный запрос
    
    
    
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
        