import customtkinter as ctk
from tkinter import messagebox

from core.contract_generator import ContractGenerator
from core.data_manager import DataManager
from pathlib import Path

# Настройка внешнего вида
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MainWindow(ctk.CTk):
    def __init__(self, base_dir=None):
        super().__init__()
        
        # Настройка основного окна
        self.title("Авто Договор")
        self.geometry("600x800")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Инициализация менеджеров
        self.data_manager = DataManager()
        self.contract_generator = ContractGenerator(self.data_manager)

        # Переменные
        self.school_type = ctk.StringVar(value="town")
        self.common_values = {
            "cost_eat": ctk.DoubleVar(value=0.0),
            "day_count": ctk.IntVar(value=0),
            "date_conclusion": ctk.StringVar(value=""),
        }
        
        # Переменные для периода
        self.period_vars = {
            "start_day": ctk.StringVar(value="1"),
            "start_month": ctk.StringVar(value="сентября"),
            "end_day": ctk.StringVar(value="31"),
            "end_month": ctk.StringVar(value="октября"),
            "year": ctk.StringVar(value="2025")
        }
        
        # Списки для выпадающих списков
        self.days = [str(i) for i in range(1, 32)]  # 1-31
        self.months = [
            "января", "февраля", "марта", "апреля", "мая", "июня",
            "июля", "августа", "сентября", "октября", "ноября", "декабря"
        ]
        
        self.schools_data = None
        self.school_vars = {}

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
        
        # Настройка вкладок
        self.setup_general_tab()
        self.setup_schools_tab()
        self.setup_generation_tab()

    def setup_general_tab(self):
        tab = self.tabview.tab("Общие настройки")
        tab.grid_columnconfigure(1, weight=1)
        
        # Основные параметры
        main_labels = ["Стоимость питания (руб):", "Количество дней:"]
        main_keys = ["cost_eat", "day_count"]
        
        for i, (label, key) in enumerate(zip(main_labels, main_keys)):
            ctk.CTkLabel(tab, text=label).grid(row=i, column=0, padx=10, pady=10, sticky="w")
            entry = ctk.CTkEntry(tab, textvariable=self.common_values[key])
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
            entry.bind('<KeyRelease>', lambda e, k=key: self.save_values())

        # Разделитель
        separator = ctk.CTkFrame(tab, height=2, fg_color="gray")
        separator.grid(row=len(main_labels), column=0, columnspan=2, sticky="ew", pady=20)
        
        # Заголовок для периода
        ctk.CTkLabel(tab, text="Период действия договора", 
                    font=ctk.CTkFont(size=14, weight="bold")).grid(
                    row=len(main_labels)+1, column=0, columnspan=2, pady=10, sticky="w")
        
        # Фрейм для периода
        period_frame = ctk.CTkFrame(tab)
        period_frame.grid(row=len(main_labels)+2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        # Компоненты строки периода
        row = 0
        
        # Нередактируемая часть: "с"
        ctk.CTkLabel(period_frame, text="с", font=ctk.CTkFont(weight="bold")).grid(
            row=row, column=0, padx=(10, 2), pady=10)
        
        # Выпадающий список: день начала (1-31)
        start_day_combo = ctk.CTkComboBox(period_frame, 
                                         values=self.days,
                                         variable=self.period_vars["start_day"],
                                         width=60,
                                         state="readonly")
        start_day_combo.grid(row=row, column=1, padx=2, pady=10)
        start_day_combo.bind('<<ComboboxSelected>>', lambda e: self.on_period_change())
        
        # Выпадающий список: месяц начала
        start_month_combo = ctk.CTkComboBox(period_frame, 
                                           values=self.months,
                                           variable=self.period_vars["start_month"],
                                           width=120,
                                           state="readonly")
        start_month_combo.grid(row=row, column=2, padx=2, pady=10)
        start_month_combo.bind('<<ComboboxSelected>>', lambda e: self.on_period_change())
        
        # Нередактируемая часть: "по"
        ctk.CTkLabel(period_frame, text="по", font=ctk.CTkFont(weight="bold")).grid(
            row=row, column=3, padx=2, pady=10)
        
        # Выпадающий список: день окончания (1-31)
        end_day_combo = ctk.CTkComboBox(period_frame, 
                                       values=self.days,
                                       variable=self.period_vars["end_day"],
                                       width=60,
                                       state="readonly")
        end_day_combo.grid(row=row, column=4, padx=2, pady=10)
        end_day_combo.bind('<<ComboboxSelected>>', lambda e: self.on_period_change())
        
        # Выпадающий список: месяц окончания
        end_month_combo = ctk.CTkComboBox(period_frame, 
                                         values=self.months,
                                         variable=self.period_vars["end_month"],
                                         width=120,
                                         state="readonly")
        end_month_combo.grid(row=row, column=5, padx=2, pady=10)
        end_month_combo.bind('<<ComboboxSelected>>', lambda e: self.on_period_change())
        
        # Поле ввода: год (только цифры)
        year_entry = ctk.CTkEntry(period_frame, textvariable=self.period_vars["year"], 
                                 width=70, justify="center")
        year_entry.grid(row=row, column=6, padx=2, pady=10)
        year_entry.bind('<KeyRelease>', lambda e: self.on_period_change())
        
        # Валидация года - только цифры
        def validate_year_input(new_value):
            return new_value.isdigit() or new_value == ""
        
        year_entry.configure(validate="key", validatecommand=(year_entry.register(validate_year_input), '%P'))
        
        # Нередактируемая часть: "года"
        ctk.CTkLabel(period_frame, text="года", font=ctk.CTkFont(weight="bold")).grid(
            row=row, column=7, padx=(2, 10), pady=10)
        
        # Отображение итоговой строки
        self.result_period_label = ctk.CTkLabel(tab, text="", font=ctk.CTkFont(size=12))
        self.result_period_label.grid(row=len(main_labels)+3, column=0, columnspan=2, pady=10, sticky="w")
        
        # Кнопки
        btn_frame = ctk.CTkFrame(tab)
        btn_frame.grid(row=len(main_labels)+4, column=0, columnspan=2, pady=20)
        
        ctk.CTkButton(btn_frame, text="Сохранить все настройки", command=self.save_values).pack(side="left", padx=10)

    def on_period_change(self):
        """Вызывается при изменении любого поля периода"""
        self.update_period_display()
        # Автоматически сохраняем в date_conclusion
        self.save_period_to_common_values()

    def update_period_display(self):
        """Обновляет отображение итоговой строки периода"""
        start_day = self.period_vars["start_day"].get()
        start_month = self.period_vars["start_month"].get()
        end_day = self.period_vars["end_day"].get()
        end_month = self.period_vars["end_month"].get()
        year = self.period_vars["year"].get()
        
        period_string = f"с {start_day} {start_month} по {end_day} {end_month} {year} года"
        self.result_period_label.configure(text=f"Текущий период: {period_string}")

    def save_period_to_common_values(self):
        """Сохраняет сформированный период в common_values"""
        start_day = self.period_vars["start_day"].get()
        start_month = self.period_vars["start_month"].get()
        end_day = self.period_vars["end_day"].get()
        end_month = self.period_vars["end_month"].get()
        year = self.period_vars["year"].get()
        
        period_string = f"с {start_day} {start_month} по {end_day} {end_month} {year} года"
        self.common_values["date_conclusion"].set(period_string)

    def parse_period_from_common_values(self):
        """Разбирает строку периода из common_values и заполняет поля"""
        period_string = self.common_values["date_conclusion"].get()
        if not period_string:
            return
            
        try:
            # Пример: "с 1 сентября по 31 октября 2025 года"
            parts = period_string.split()
            if len(parts) >= 8:
                # Извлекаем компоненты
                start_day = parts[1]
                start_month = parts[2]
                end_day = parts[4]
                end_month = parts[5]
                year = parts[6]
                
                # Устанавливаем значения в переменные
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
                
        except Exception as e:
            print(f"Ошибка разбора периода: {e}")

    # Остальные методы остаются без изменений
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

    def load_initial_data(self):
        """Загрузка начальных данных"""
        self.load_values()
        self.schools_data = self.data_manager.load_schools_config()
        if self.schools_data:
            self.update_schools_display()
        else:
            messagebox.showerror("Ошибка", "Не удалось загрузить конфигурацию школ!")

        # После загрузки common_values разбираем период
        self.parse_period_from_common_values()

    def update_schools_display(self):
        """Обновление отображения школ с placeholder"""
        if not self.schools_data:
            return

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
            
            default_value = str(school.get('child_count', 0))
            school_var = ctk.StringVar(value="")
            self.school_vars[school['id']] = school_var
            
            school_entry = ctk.CTkEntry(
                self.schools_table_frame, 
                textvariable=school_var, 
                width=80,
                placeholder_text=default_value,
                placeholder_text_color="gray60"
            )
            school_entry.grid(row=row, column=1, padx=5, pady=5)
            
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

    def save_values(self):
        """Сохранение значений в файл"""
        # Убедимся, что период тоже сохранен
        self.save_period_to_common_values()
        
        common_values_dict = {
            "cost_eat": self.common_values["cost_eat"].get(),
            "day_count": self.common_values["day_count"].get(),
            "date_conclusion": self.common_values["date_conclusion"].get(),
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

            # Убедимся, что период сохранен перед генерацией
            self.save_period_to_common_values()

            if not all([self.common_values[key].get() for key in self.common_values]):
                messagebox.showwarning("Внимание", "Заполните все общие параметры!")
                return

            if not self.schools_data:
                messagebox.showerror("Ошибка", "Данные о школах не загружены!")
                return

            common_values_dict = {
                "cost_eat": self.common_values["cost_eat"].get(),
                "day_count": self.common_values["day_count"].get(),
                "date_conclusion": self.common_values["date_conclusion"].get(),
                
            }

            def progress_callback(progress):
                self.progress_bar.set(progress)
                self.update()

            def log_callback(message):
                self.log_text.insert("end", message + "\n")
                self.log_text.see("end")
                self.update()

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

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()