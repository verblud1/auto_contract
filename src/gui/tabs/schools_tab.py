import customtkinter as ctk

class SchoolsTab:
    """Вкладка управления школами"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.create_widgets()
        
    def create_widgets(self):
        """Создание виджетов вкладки"""
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(1, weight=1)
        
        # Фрейм типа школ
        self.create_type_frame()
        
        # Таблица школ
        self.create_schools_table()
    
    def create_type_frame(self):
        """Создание фрейма выбора типа школ"""
        type_frame = ctk.CTkFrame(self.parent)
        type_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(type_frame, text="Тип школ:").pack(side="left", padx=10)
        ctk.CTkRadioButton(type_frame, text="Город", 
                          variable=self.main_window.school_type, 
                          value="town", 
                          command=self.main_window.on_school_type_change).pack(side="left", padx=10)
        ctk.CTkRadioButton(type_frame, text="Район", 
                          variable=self.main_window.school_type, 
                          value="district", 
                          command=self.main_window.on_school_type_change).pack(side="left", padx=10)
    
    def create_schools_table(self):
        """Создание таблицы школ"""
        self.schools_table_frame = ctk.CTkScrollableFrame(self.parent)
        self.schools_table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.schools_table_frame.grid_columnconfigure(0, weight=1)
    
    def update_schools_display(self, schools):
        """Обновление отображения школ"""
        # Очистка текущего отображения
        for widget in self.schools_table_frame.winfo_children():
            widget.destroy()

        self.main_window.school_vars = {}
      
        # Заголовки таблицы
        headers = ["Школа", "Кол-во детей"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(self.schools_table_frame, text=header, 
                        font=ctk.CTkFont(weight="bold")).grid(
                        row=0, column=i, padx=5, pady=5, sticky="ew")

        # Данные школ
        for row, school in enumerate(schools, 1):
            ctk.CTkLabel(self.schools_table_frame, text=school['name']).grid(
                row=row, column=0, padx=5, pady=5, sticky="w")
            
            default_value = str(school.get('child_count', 0))
            school_var = ctk.StringVar(value="")
            self.main_window.school_vars[school['id']] = school_var
            
            school_entry = ctk.CTkEntry(
                self.schools_table_frame, 
                textvariable=school_var, 
                width=80,
                placeholder_text=default_value,
                placeholder_text_color="gray60"
            )
            school_entry.grid(row=row, column=1, padx=5, pady=5)
            
            school_entry.bind('<KeyRelease>', 
                lambda event, s=school, var=school_var: self.main_window.set_child_count(s, var.get()))

        self.schools_table_frame.grid_columnconfigure(0, weight=1)
        self.schools_table_frame.grid_columnconfigure(1, weight=0)