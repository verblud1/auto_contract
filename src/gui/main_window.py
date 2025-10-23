import customtkinter as ctk
from tkinter import messagebox

from core.contract_generator import ContractGenerator
from core.data_manager import DataManager
from core.config import Config

from gui.tabs.general_tab import GeneralTab
from gui.tabs.schools_tab import SchoolsTab
from gui.tabs.generation_tab import GenerationTab

class MainWindow(ctk.CTk):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        
        # Инициализация конфигурации
        self.config = Config()
        
        # Настройка основного окна
        self.setup_window()
        
        # Инициализация менеджеров
        self.data_manager = DataManager()
        self.contract_generator = ContractGenerator(self.data_manager)
        
        # Инициализация переменных
        self.init_variables()
        
        # Проверка инициализации common_values
        print("Инициализированные common_values ключи:", list(self.common_values.keys()))
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка данных
        self.load_initial_data()
    
    def setup_window(self):
        """Настройка главного окна"""
        self.title("Авто Договор")
        self.geometry("600x800")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
    
    def init_variables(self):
        """Инициализация переменных"""
        self.school_type = ctk.StringVar(value="town")
        self.common_values = {
            "cost_eat": ctk.DoubleVar(value=0.0),
            "day_count": ctk.IntVar(value=0),
            "date_conclusion": ctk.StringVar(value=""),
        }
        
        self.period_vars = {
            "start_day": ctk.StringVar(value="1"),
            "start_month": ctk.StringVar(value="сентября"),
            "end_day": ctk.StringVar(value="31"),
            "end_month": ctk.StringVar(value="октября"),
            "year": ctk.StringVar(value="2025")
        }
        
        self.days = self.config.days
        self.months = self.config.months
        
        self.schools_data = None
        self.school_vars = {}
    
    def create_widgets(self):
        """Создание виджетов"""
        # Создание вкладок
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Добавление вкладок
        self.tabview.add("Общие настройки")
        self.tabview.add("Школы")
        self.tabview.add("Генерация")
        
        # Создание вкладок
        self.general_tab = GeneralTab(self.tabview.tab("Общие настройки"), self)
        self.schools_tab = SchoolsTab(self.tabview.tab("Школы"), self)
        self.generation_tab = GenerationTab(self.tabview.tab("Генерация"), self)

    def on_period_change(self):
        """Вызывается при изменении любого поля периода"""
        self.update_period_display()
        self.save_period_to_common_values()

    def update_period_display(self):
        """Обновляет отображение итоговой строки периода"""
        period_string = self.get_period_string()
        self.general_tab.update_period_display(period_string)

    def get_period_string(self):
        """Получение строки периода"""
        start_day = self.period_vars["start_day"].get()
        start_month = self.period_vars["start_month"].get()
        end_day = self.period_vars["end_day"].get()
        end_month = self.period_vars["end_month"].get()
        year = self.period_vars["year"].get()
        
        return f"с {start_day} {start_month} по {end_day} {end_month} {year} года"

    def save_period_to_common_values(self):
        """Сохраняет сформированный период в common_values"""
        try:
            # Получаем строки периода и даты из виджета
            period_string = self.general_tab.period_selector.get_period_string()
            date_string = self.general_tab.period_selector.get_date_string()
            year = self.period_vars["year"].get()
            
            # Устанавливаем значения в common_values с проверкой наличия ключей
            self.common_values["date_conclusion"].set(period_string)
            
            # Проверяем и устанавливаем date, если ключ существует
            if "date" in self.common_values:
                self.common_values["date"].set(date_string)
            else:
                print("Предупреждение: ключ 'date' отсутствует в common_values")
                
            # Проверяем и устанавливаем year, если ключ существует  
            if "year" in self.common_values:
                self.common_values["year"].set(year)
            else:
                print("Предупреждение: ключ 'year' отсутствует в common_values")
            
            print(f"Сохранен период: {period_string}")
            print(f"Сохранена дата: {date_string}")
            print(f"Сохранен год: {year}")
        
        except Exception as e:
            print(f"Ошибка при сохранении периода: {e}")

    def parse_period_from_common_values(self):
        """Разбирает строку периода из common_values и заполняет поля"""
        # Проверяем наличие ключа date_conclusion
        if "date_conclusion" not in self.common_values:
            print("Ключ 'date_conclusion' отсутствует в common_values")
            return
            
        period_string = self.common_values["date_conclusion"].get()
        if not period_string:
            print("Период не найден в common_values")
            return
            
        try:
            print(f"Разбираем период: '{period_string}'")
            
            # Пример: "с 1 сентября по 31 октября 2025 года"
            parts = period_string.split()
            if len(parts) >= 8:
                # Извлекаем компоненты
                start_day = parts[1]
                start_month = parts[2]
                end_day = parts[4]
                end_month = parts[5]
                year = parts[6]
                
                # Устанавливаем значения в переменные периода
                if start_day in self.days:
                    self.period_vars["start_day"].set(start_day)
                if start_month in self.months:
                    self.period_vars["start_month"].set(start_month)
                if end_day in self.days:
                    self.period_vars["end_day"].set(end_day)
                if end_month in self.months:
                    self.period_vars["end_month"].set(end_month)
                self.period_vars["year"].set(year)
                
                # Обновляем отображение
                self.update_period_display()
                
                print(f"Разобрали период: start_day={start_day}, start_month={start_month}, end_day={end_day}, end_month={end_month}, year={year}")
            else:
                print(f"Не удалось разобрать период: неожиданное количество частей ({len(parts)})")
                
        except Exception as e:
            print(f"Ошибка разбора периода: {e}")

    def load_values(self):
        """Загрузка общих значений из файла"""
        common_values_dict = self.data_manager.load_common_values()
        for key, value in common_values_dict.items():
            if key in self.common_values:
                self.common_values[key].set(value)
            else:
                print(f"Предупреждение: ключ '{key}' отсутствует в common_values, но присутствует в файле")

    def update_schools_display(self):
        """Обновление отображения школ с placeholder"""
        if not self.schools_data:
            return

        schools = self.schools_data[0]["schools"][self.school_type.get()]
        self.schools_tab.update_schools_display(schools)

    def set_child_count(self, school, value):
        """Установка количества детей для школы"""
        try:
            child_count = int(value) if value else 0
            self.data_manager.update_school_child_count(
                self.schools_data, self.school_type.get(), school['id'], child_count
            )
        except ValueError:
            pass

    def load_values(self):
        """Загрузка общих значений из файла"""
        common_values_dict = self.data_manager.load_common_values()
        for key, value in common_values_dict.items():
            if key in self.common_values:
                self.common_values[key].set(value)

    def save_values(self):
        """Сохранение значений в файл"""
        # Убедимся, что период тоже сохранен
        self.save_period_to_common_values()
        
        # Создаем словарь только с существующими ключами
        common_values_dict = {}
        for key in ["cost_eat", "day_count", "date_conclusion", "date", "year"]:
            if key in self.common_values:
                common_values_dict[key] = self.common_values[key].get()
            else:
                print(f"Предупреждение: ключ '{key}' отсутствует при сохранении")
        
        if self.data_manager.save_common_values(common_values_dict):
            messagebox.showinfo("Успех", "Данные сохранены!")
        else:
            messagebox.showerror("Ошибка", "Ошибка сохранения данных!")

    def generate_contracts(self):
        """Генерация договоров"""
        #try:
        self.generation_tab.clear_log()
        self.generation_tab.log_message("Начало генерации договоров...")
        self.update()

            # Убедимся, что период сохранен перед генерацией
        self.save_period_to_common_values()

            # Проверка заполнения обязательных полей
        required_fields = ["cost_eat", "day_count", "date_conclusion", "date", "year"]
        missing_fields = []
            
        for field in required_fields:
            vextalue = self.common_values[field].get()
            if not value:
                missing_fields.append(field)
            
        if missing_fields:
            messagebox.showwarning("Внимание", f"Заполните все общие параметры! Отсутствуют: {', '.join(missing_fields)}")
            return

        if not self.schools_data:
            messagebox.showerror("Ошибка", "Данные о школах не загружены!")
            return

        # Подготовка данных для генерации
        common_values_dict = {
            "cost_eat": self.common_values["cost_eat"].get(),
            "day_count": self.common_values["day_count"].get(),
            "date_conclusion": self.common_values["date_conclusion"].get(),
            "date": self.common_values["date"].get(),
            "year": self.common_values["year"].get()
        }

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
     
        #except Exception as e:
        #    messagebox.showerror("Ошибка", f"Ошибка генерации: {str(e)}")
         #   self.generation_tab.log_message(f"Критическая ошибка: {str(e)}\n")
            
    def get_current_date(self):
        """Получение текущей даты в формате дд.мм.гггг"""
        from datetime import datetime
        return datetime.now().strftime("%d.%m.%Y")

    def on_school_type_change(self):
        """Обработчик изменения типа школ"""
        self.update_schools_display()