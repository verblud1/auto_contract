import customtkinter as ctk

class GenerationTab:
    """Вкладка генерации договоров"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.create_widgets()
        
    def create_widgets(self):
        """Создание виджетов вкладки"""
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(1, weight=1)
        
        # Лог выполнения
        self.create_log_section()
        
        # Прогресс бар
        self.create_progress_bar()
        
        # Кнопка генерации
        self.create_generate_button()
    
    def create_log_section(self):
        """Создание секции лога"""
        ctk.CTkLabel(self.parent, text="Лог выполнения:").grid(
            row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.log_text = ctk.CTkTextbox(self.parent, height=200)
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
    
    def create_progress_bar(self):
        """Создание прогресс бара"""
        self.progress_bar = ctk.CTkProgressBar(self.parent)
        self.progress_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        self.progress_bar.set(0)
    
    def create_generate_button(self):
        """Создание кнопки генерации"""
        ctk.CTkButton(self.parent, text="Сгенерировать договоры", 
                     command=self.main_window.generate_contracts,
                     fg_color="green", hover_color="dark green").grid(
                     row=3, column=0, pady=20)
    
    def log_message(self, message):
        """Добавление сообщения в лог"""
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.parent.update()
    
    def clear_log(self):
        """Очистка лога"""
        self.log_text.delete("1.0", "end")
    
    def set_progress(self, value):
        """Установка значения прогресса"""
        self.progress_bar.set(value)
        self.parent.update()