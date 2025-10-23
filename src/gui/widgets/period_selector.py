import customtkinter as ctk

class PeriodSelector(ctk.CTkFrame):
    """Виджет для выбора периода"""
    
    def __init__(self, parent, days, months, period_vars, change_callback):
        super().__init__(parent)
        self.days = days
        self.months = months
        self.period_vars = period_vars
        self.change_callback = change_callback
        
        self.create_widgets()
        
    def create_widgets(self):
        """Создание виджетов периода"""
        # Нередактируемая часть: "с"
        ctk.CTkLabel(self, text="с", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=(10, 2), pady=10)
        
        # Выпадающий список: день начала (1-31)
        self.start_day_combo = ctk.CTkComboBox(self, 
                                         values=self.days,
                                         variable=self.period_vars["start_day"],
                                         width=60,
                                         state="readonly")
        self.start_day_combo.grid(row=0, column=1, padx=2, pady=10)
        self.start_day_combo.bind('<<ComboboxSelected>>', self.on_period_change)
        
        # Выпадающий список: месяц начала
        self.start_month_combo = ctk.CTkComboBox(self, 
                                           values=self.months,
                                           variable=self.period_vars["start_month"],
                                           width=120,
                                           state="readonly")
        self.start_month_combo.grid(row=0, column=2, padx=2, pady=10)
        self.start_month_combo.bind('<<ComboboxSelected>>', self.on_period_change)
        
        # Нередактируемая часть: "по"
        ctk.CTkLabel(self, text="по", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=3, padx=2, pady=10)
        
        # Выпадающий список: день окончания (1-31)
        self.end_day_combo = ctk.CTkComboBox(self, 
                                       values=self.days,
                                       variable=self.period_vars["end_day"],
                                       width=60,
                                       state="readonly")
        self.end_day_combo.grid(row=0, column=4, padx=2, pady=10)
        self.end_day_combo.bind('<<ComboboxSelected>>', self.on_period_change)
        
        # Выпадающий список: месяц окончания
        self.end_month_combo = ctk.CTkComboBox(self, 
                                         values=self.months,
                                         variable=self.period_vars["end_month"],
                                         width=120,
                                         state="readonly")
        self.end_month_combo.grid(row=0, column=5, padx=2, pady=10)
        self.end_month_combo.bind('<<ComboboxSelected>>', self.on_period_change)
        
        # Поле ввода: год (только цифры)
        self.year_entry = ctk.CTkEntry(self, textvariable=self.period_vars["year"], 
                                 width=70, justify="center")
        self.year_entry.grid(row=0, column=6, padx=2, pady=10)
        self.year_entry.bind('<KeyRelease>', self.on_period_change)
        
        # Валидация года - только цифры
        def validate_year_input(new_value):
            return new_value.isdigit() or new_value == ""
        
        self.year_entry.configure(validate="key", 
                                validatecommand=(self.year_entry.register(validate_year_input), '%P'))
        
        # Нередактируемая часть: "года"
        ctk.CTkLabel(self, text="года", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=7, padx=(2, 10), pady=10)
    
    def on_period_change(self, event=None):
        """Обработчик изменения периода"""
        self.change_callback()
    
    def get_period_string(self):
        """Получение строки периода"""
        start_day = self.period_vars["start_day"].get()
        start_month = self.period_vars["start_month"].get()
        end_day = self.period_vars["end_day"].get()
        end_month = self.period_vars["end_month"].get()
        year = self.period_vars["year"].get()
        
        return f"с {start_day} {start_month} по {end_day} {end_month} {year} года"
    
    def get_date_string(self):
        """Получение строки даты (только начало периода)"""
        start_day = self.period_vars["start_day"].get()
        start_month = self.period_vars["start_month"].get()
        year = self.period_vars["year"].get()
        
        return f"{start_day} {start_month} {year} года"