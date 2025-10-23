import customtkinter as ctk
from tkinter import messagebox
from gui.widgets.period_selector import PeriodSelector

class GeneralTab:
    """Вкладка общих настроек"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.create_widgets()
        
    def create_widgets(self):
        """Создание виджетов вкладки"""
        self.parent.grid_columnconfigure(1, weight=1)
        
        # Основные параметры
        self.create_main_parameters()
        
        # Разделитель
        self.create_separator()
        
        # Период действия договора
        self.create_period_section()
        
        # Кнопки
        self.create_buttons()
    
    def create_main_parameters(self):
        """Создание основных параметров"""
        main_labels = ["Стоимость питания (руб):", "Количество дней:"]
        main_keys = ["cost_eat", "day_count"]
        
        for i, (label, key) in enumerate(zip(main_labels, main_keys)):
            ctk.CTkLabel(self.parent, text=label).grid(row=i, column=0, padx=10, pady=10, sticky="w")
            entry = ctk.CTkEntry(self.parent, textvariable=self.main_window.common_values[key])
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
            entry.bind('<KeyRelease>', lambda e, k=key: self.main_window.save_values())
    
    def create_separator(self):
        """Создание разделителя"""
        separator = ctk.CTkFrame(self.parent, height=2, fg_color="gray")
        separator.grid(row=2, column=0, columnspan=2, sticky="ew", pady=20)
    
    def create_period_section(self):
        """Создание секции периода"""
        # Заголовок для периода
        ctk.CTkLabel(self.parent, text="Период действия договора", 
                    font=ctk.CTkFont(size=14, weight="bold")).grid(
                    row=3, column=0, columnspan=2, pady=10, sticky="w")
        
        # Виджет выбора периода
        self.period_selector = PeriodSelector(
            self.parent, 
            self.main_window.days,
            self.main_window.months,
            self.main_window.period_vars,
            self.main_window.on_period_change
        )
        self.period_selector.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        # Отображение итоговой строки
        self.result_period_label = ctk.CTkLabel(self.parent, text="", font=ctk.CTkFont(size=12))
        self.result_period_label.grid(row=5, column=0, columnspan=2, pady=10, sticky="w")
    
    def create_buttons(self):
        """Создание кнопок"""
        btn_frame = ctk.CTkFrame(self.parent)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ctk.CTkButton(btn_frame, text="Сохранить все настройки", 
                     command=self.main_window.save_values).pack(side="left", padx=10)
    
    def update_period_display(self, period_string):
        """Обновление отображения периода"""
        self.result_period_label.configure(text=f"Текущий период: {period_string}")