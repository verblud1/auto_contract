import customtkinter as ctk
from tkinter import messagebox

# Настройка внешнего вида
ctk.set_appearance_mode("System")  # Режим: "Light", "Dark" или "System"
ctk.set_default_color_theme("green")  # Темы: "blue", "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Настройка основного окна
        self.title("Авто Договор")
        self.geometry("600x400")
        
        # Создание виджетов
        self.create_widgets()
    
    def create_widgets(self):
        # Метка
        self.label = ctk.CTkLabel(self, 
                                 text="Добро пожаловать в CustomTkinter!",
                                 font=ctk.CTkFont(size=16, weight="bold"))
        self.label.pack(pady=20)
        
        # Поле ввода
        self.entry = ctk.CTkEntry(self, 
                                 placeholder_text="Введите текст здесь",
                                 width=300)
        self.entry.pack(pady=10)
        
        # Кнопка
        self.button = ctk.CTkButton(self, 
                                   text="Нажми меня",
                                   command=self.button_callback)
        self.button.pack(pady=10)
        
        # Переключатель тем
        self.theme_switch = ctk.CTkSwitch(self,
                                         text="Темная тема",
                                         command=self.toggle_theme)
        self.theme_switch.pack(pady=20)
        
        # Выпадающий список
        self.combobox = ctk.CTkComboBox(self,
                                       values=["Вариант 1", "Вариант 2", "Вариант 3"])
        self.combobox.pack(pady=10)
        
        # Ползунок
        self.slider = ctk.CTkSlider(self,
                                   from_=0,
                                   to=100,
                                   number_of_steps=10)
        self.slider.pack(pady=10)
        
    def button_callback(self):
        text = self.entry.get()
        messagebox.showinfo("Уведомление", f"Вы ввели: {text}")
    
    def toggle_theme(self):
        if self.theme_switch.get():
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

if __name__ == "__main__":
    app = App()
    app.mainloop()