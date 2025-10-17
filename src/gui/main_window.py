import customtkinter as ctk
from tkinter import messagebox

from core.contract_generator import ContractGenerator
from core.data_manager import DataManager
from pathlib import Path

# Настройка внешнего вида
ctk.set_appearance_mode("System")  # Режим: "Light", "Dark" или "System"
ctk.set_default_color_theme("blue")  # Темы: "blue", "green", "dark-blue"

class MainWindow(ctk.CTk):
    def __init__(self, base_dir=None):
        super().__init__()
        
        #Установка путей до файлов
        #if base_dir is None:
         #   base_dir = Path(__file__).parent.parent
        #self.icon_dir =  base_dir / 'images' / 'icon' / 'icon.ico'

        # Настройка основного окна
        self.title("Авто Договор")
        self.geometry("500x700")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        #self.iconbitmap(self.icon_dir)

        # Инициализация менеджеров
        self.data_manager = DataManager()
        self.contract_generator = ContractGenerator(self.data_manager)

        # Переменные
        self.school_type = ctk.StringVar(value="town") # тип школы по умолчанию город, если отличается - район
        self.common_values = {
            "cost_eat": ctk.DoubleVar(value=0.0),
            "day_count": ctk.IntVar(value=0),
            "date": ctk.StringVar(value=""),
            "date_conclusion": ctk.StringVar(value=""),
            "year": ctk.StringVar(value="")
        }
        
        self.schools_data = None
        self.school_vars = {}  # Для хранения переменных школ

        self.create_widgets()
        self.load_initial_data()

    def create_widgets(self):
        # Создание вкладок
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Добавление вкладок
        self.tabview.add("Общие настройки")
        self.tabview.add("Школы")
        self.tabview.add("Генерация")
        self.tabview.add("Допники")
        self.tabview.add("Лагерь")
        
        # Настройка вкладок
        self.setup_general_tab()
        self.setup_schools_tab()
        self.setup_generation_tab()
        self.setup_additional_agr_tab()

    def setup_general_tab(self):
        tab = self.tabview.tab("Общие настройки")
        
        labels = ["Стоимость питания (руб):", "Количество дней:", "Дата:", "Дата заключения:", "Год:"]
        keys = ["cost_eat", "day_count", "date", "date_conclusion", "year"]
        
        for i, (label, key) in enumerate(zip(labels, keys)):
            ctk.CTkLabel(tab, text=label).grid(row=i, column=0, padx=10, pady=10, sticky="w")
            entry = ctk.CTkEntry(tab, textvariable=self.common_values[key])
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")

        btn_frame = ctk.CTkFrame(tab)
        btn_frame.grid(row=len(labels), column=0, columnspan=2, pady=20)
        

        ctk.CTkButton(btn_frame, text="Сохранить", command=self.save_values).pack(side="left", padx=10)
        
        tab.grid_columnconfigure(1, weight=1)

    def setup_schools_tab(self):
        tab = self.tabview.tab("Школы")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        type_frame = ctk.CTkFrame(tab)
        type_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(type_frame, text="Тип школ:").pack(side="left", padx=10)
        ctk.CTkRadioButton(type_frame, text="Город", variable=self.school_type, 
                          value="town", command=self.update_schools_display).pack(side="left", padx=10)
        ctk.CTkRadioButton(type_frame, text="Район", variable=self.school_type, 
                          value="district", command=self.update_schools_display).pack(side="left", padx=10)
        
        self.schools_table_frame = ctk.CTkScrollableFrame(tab)
        self.schools_table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.schools_table_frame.grid_columnconfigure(0, weight=1)

    def setup_generation_tab(self):
        tab = self.tabview.tab("Генерация")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(tab, text="Лог выполнения:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.log_text = ctk.CTkTextbox(tab, height=200)
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(tab)
        self.progress_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        self.progress_bar.set(0)
        
        ctk.CTkButton(tab, text="Сгенерировать договоры", command=self.generate_contracts,
                     fg_color="green", hover_color="dark green").grid(row=3, column=0, pady=20)
    

    def setup_additional_agr_tab(self):
        """Загрузка допников"""
        
        tab = self.tabview.tab("Допники")
        tab.grid_columnconfigure(0,weight=1)
        tab.grid_rowconfigure(1,weight=1)
        type_frame = ctk.CTkFrame(tab)
        type_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(type_frame, text="Допники").pack(side="left", padx=10)


    def load_initial_data(self):
        """Загрузка начальных данных"""

        # Загрузка common_values
        self.load_values()


        # Загрузка конфига школ
        self.schools_data = self.data_manager.load_schools_config()
        if self.schools_data:
            self.update_schools_display()
        else:
            messagebox.showerror("Ошибка", "Не удалось загрузить конфигурацию школ!")


    def update_schools_display(self):
        """Обновление отображения школ с placeholder"""
        if not self.schools_data:
            return

        # Очистка предыдущего отображения
        for widget in self.schools_table_frame.winfo_children():
            widget.destroy()

        self.school_vars = {}
      
        headers = ["Школа", "Кол-во детей"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(self.schools_table_frame, text=header, font=ctk.CTkFont(weight="bold")).grid(
                row=0, column=i, padx=5, pady=5, sticky="ew")

        schools = self.schools_data[0]["schools"][self.school_type.get()]
        for row, school in enumerate(schools, 1):
            ctk.CTkLabel(self.schools_table_frame, text=school['name']).grid(
                row=row, column=0, padx=5, pady=5, sticky="w")
            
            # Получаем значение по умолчанию из конфига
            default_value = str(school.get('child_count', 0))
            
            # Создаем переменную с пустым значением
            school_var = ctk.StringVar(value="")
            
            # Сохраняем ссылку на переменную
            self.school_vars[school['id']] = school_var
            
            # Создаем поле ввода с placeholder
            school_entry = ctk.CTkEntry(
                self.schools_table_frame, 
                textvariable=school_var, 
                width=80,
                placeholder_text=default_value,  # Фоновый текст
                placeholder_text_color="gray60"   # Цвет фонового текста
            )
            school_entry.grid(row=row, column=1, padx=5, pady=5)
            
            # Обработчик ввода
            school_entry.bind('<KeyRelease>', 
                lambda event, s=school, var=school_var: self.set_child_count(s, var.get()))

        self.schools_table_frame.grid_columnconfigure(0, weight=1)
        self.schools_table_frame.grid_columnconfigure(1, weight=0)

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
        messagebox.showinfo("Успех", "Данные загружены!")

    def save_values(self):
        """Сохранение значений в файл"""
        common_values_dict = {
            "cost_eat": self.common_values["cost_eat"].get(),
            "day_count": self.common_values["day_count"].get(),
            "date": self.common_values["date"].get(),
            "date_conclusion": self.common_values["date_conclusion"].get(),
            "year": self.common_values["year"].get()
        }
        
        if self.data_manager.save_common_values(common_values_dict):
            messagebox.showinfo("Успех", "Данные сохранены!")
        else:
            messagebox.showerror("Ошибка", "Ошибка сохранения данных!")

    def generate_contracts(self):
        """Генерация договоров"""
        try:
            self.log_text.delete("1.0", "end")
            self.log_text.insert("end", "Начало генерации договоров...\n")
            self.update()

            # Проверка заполнения
            if not all([self.common_values[key].get() for key in self.common_values]):
                messagebox.showwarning("Внимание", "Заполните все общие параметры!")
                return

            if not self.schools_data:
                messagebox.showerror("Ошибка", "Данные о школах не загружены!")
                return

            # Подготовка данных
            common_values_dict = {
                "cost_eat": self.common_values["cost_eat"].get(),
                "day_count": self.common_values["day_count"].get(),
                "date": self.common_values["date"].get(),
                "date_conclusion": self.common_values["date_conclusion"].get(),
                "year": self.common_values["year"].get()
            }

            # Колбэки для прогресса и логирования
            def progress_callback(progress):
                self.progress_bar.set(progress)
                self.update()

            def log_callback(message):
                self.log_text.insert("end", message + "\n")
                self.log_text.see("end")
                self.update()

            # Запуск генерации
            successful_count, total_schools = self.contract_generator.generate_contracts(
                common_values_dict,
                self.schools_data,
                self.school_type.get(),
                progress_callback,
                log_callback
            )

            self.log_text.insert("end", f"\nГенерация завершена! Успешно: {successful_count}/{total_schools}\n")
            messagebox.showinfo("Успех", f"Договоры сгенерированы! Успешно: {successful_count}/{total_schools}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации: {str(e)}")
            self.log_text.insert("end", f"Критическая ошибка: {str(e)}\n")