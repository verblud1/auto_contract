import customtkinter as ctk
from tkinter import messagebox, ttk
import json
from pathlib import Path
import os

class ContractAuto_App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Настройка основного окна
        self.title("Авто Договор")
        self.geometry("1000x700")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Переменные
        self.script_dir = Path(__file__).parent
        self.parent_dir = self.script_dir.parent
        self.templates_dir = self.parent_dir / "templates"
        self.output_dir = self.parent_dir.parent / "schools_output"
        
        self.schools_data = []
        self.current_school_type = ctk.StringVar(value="town")
        self.type_name_ru = ctk.StringVar(value="Город")
        
        # Основные переменные
        self.common_values = {
            "cost_eat": ctk.DoubleVar(value=0.0),
            "day_count": ctk.IntVar(value=0),
            "date": ctk.StringVar(value=""),
            "date_conclusion": ctk.StringVar(value=""),
            "year": ctk.StringVar(value="")
        }
        
        self.create_widgets()
        self.load_data()

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
        
        # Поля для общих значений
        labels = ["Стоимость питания (руб):", "Количество дней:", "Дата:", "Дата заключения:", "Год:"]
        keys = ["cost_eat", "day_count", "date", "date_conclusion", "year"]
        
        for i, (label, key) in enumerate(zip(labels, keys)):
            ctk.CTkLabel(tab, text=label).grid(row=i, column=0, padx=10, pady=10, sticky="w")
            entry = ctk.CTkEntry(tab, textvariable=self.common_values[key])
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
        
        # Кнопки загрузки/сохранения
        btn_frame = ctk.CTkFrame(tab)
        btn_frame.grid(row=len(labels), column=0, columnspan=2, pady=20)
        
        ctk.CTkButton(btn_frame, text="Загрузить из файла", command=self.load_values).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Сохранить в файл", command=self.save_values).pack(side="left", padx=10)
        
        tab.grid_columnconfigure(1, weight=1)

    def setup_schools_tab(self):
        tab = self.tabview.tab("Школы")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # Выбор типа школ
        type_frame = ctk.CTkFrame(tab)
        type_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(type_frame, text="Тип школ:").pack(side="left", padx=10)
        ctk.CTkRadioButton(type_frame, text="Город", variable=self.current_school_type, 
                          value="town", command=self.update_schools_display).pack(side="left", padx=10)
        ctk.CTkRadioButton(type_frame, text="Район", variable=self.current_school_type, 
                          value="district", command=self.update_schools_display).pack(side="left", padx=10)
        
        # Таблица школ
        self.schools_table_frame = ctk.CTkScrollableFrame(tab)
        self.schools_table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Кнопка добавления школы
        ctk.CTkButton(tab, text="Добавить школу", command=self.add_school).grid(row=2, column=0, pady=10)

    def setup_generation_tab(self):
        tab = self.tabview.tab("Генерация")
        tab.grid_columnconfigure(0, weight=1)
        
        # Лог генерации
        ctk.CTkLabel(tab, text="Лог выполнения:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.log_text = ctk.CTkTextbox(tab, height=200)
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Прогресс бар
        self.progress_bar = ctk.CTkProgressBar(tab)
        self.progress_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        self.progress_bar.set(0)
        
        # Кнопка генерации
        ctk.CTkButton(tab, text="Сгенерировать договоры", command=self.generate_contracts,
                     fg_color="green", hover_color="dark green").grid(row=3, column=0, pady=20)

    def update_schools_display(self):
        # Очистка предыдущего отображения
        for widget in self.schools_table_frame.winfo_children():
            widget.destroy()
        
        # Заголовки таблицы (с кла)
        headers = ["Школа", "Кол-во детей 1-4 кл.", "Кол-во детей 5-11 кл.", "Всего", "Действия"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(self.schools_table_frame, text=header, font=ctk.CTkFont(weight="bold")).grid(
                row=0, column=i, padx=5, pady=5)
        
        # Данные школ
        schools = self.schools_data[0]["schools"][self.current_school_type.get()]
        for row, school in enumerate(schools, 1):
            # Название школы
            ctk.CTkLabel(self.schools_table_frame, text=school['name']).grid(
                row=row, column=0, padx=5, pady=5)
            
            # Поля для ввода количества детей
            primary_var = ctk.IntVar(value=school.get('primary_count', 0))
            secondary_var = ctk.IntVar(value=school.get('secondary_count', 0))
            total_var = ctk.IntVar(value=primary_var.get() + secondary_var.get())
            
            primary_entry = ctk.CTkEntry(self.schools_table_frame, textvariable=primary_var, width=80)
            primary_entry.grid(row=row, column=1, padx=5, pady=5)
            primary_entry.bind('<KeyRelease>', lambda e, p=primary_var, s=secondary_var, t=total_var: 
                             self.update_total(p, s, t))
            
            secondary_entry = ctk.CTkEntry(self.schools_table_frame, textvariable=secondary_var, width=80)
            secondary_entry.grid(row=row, column=2, padx=5, pady=5)
            secondary_entry.bind('<KeyRelease>', lambda e, p=primary_var, s=secondary_var, t=total_var: 
                               self.update_total(p, s, t))
            
            # Общее количество
            total_label = ctk.CTkLabel(self.schools_table_frame, textvariable=total_var)
            total_label.grid(row=row, column=3, padx=5, pady=5)
            
            # Кнопки действий
            btn_frame = ctk.CTkFrame(self.schools_table_frame, fg_color="transparent")
            btn_frame.grid(row=row, column=4, padx=5, pady=5)
            
            ctk.CTkButton(btn_frame, text="✏️", width=30, height=30,
                         command=lambda s=school: self.edit_school(s)).pack(side="left", padx=2)
            ctk.CTkButton(btn_frame, text="🗑️", width=30, height=30, fg_color="red", hover_color="dark red",
                         command=lambda s=school: self.delete_school(s)).pack(side="left", padx=2)

    def update_total(self, primary_var, secondary_var, total_var):
        try:
            total = primary_var.get() + secondary_var.get()
            total_var.set(total)
        except:
            total_var.set(0)

    def load_data(self):
        """Загрузка данных из файлов"""
        try:
            # Загрузка common_values
            values_file = self.parent_dir.parent / 'common_values.txt'
            if values_file.exists():
                with open(values_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            if key == "Стоимость дня":
                                self.common_values["cost_eat"].set(float(value))
                            elif key == "Кол-во дней":
                                self.common_values["day_count"].set(int(value))
                            elif key == "Дата":
                                self.common_values["date"].set(value)
                            elif key == "Дата заключения договора":
                                self.common_values["date_conclusion"].set(value)
                            elif key == "Год":
                                self.common_values["year"].set(value)
            
            # Загрузка конфига школ
            config_file = self.parent_dir / "data" / "config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.schools_data = json.load(f)
                
                self.update_schools_display()
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки данных: {str(e)}")

    def generate_contracts(self):
        """Генерация договоров"""
        try:
            self.log_text.delete("1.0", "end")
            self.log_text.insert("end", "Начало генерации договоров...\n")
            
            # Здесь будет ваша основная логика генерации
            # Для начала просто проверим данные
            
            if not all([self.common_values[key].get() for key in self.common_values]):
                messagebox.showwarning("Внимание", "Заполните все общие параметры!")
                return
                
            self.log_text.insert("end", "Генерация завершена успешно!\n")
            messagebox.showinfo("Успех", "Договоры успешно сгенерированы!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации: {str(e)}")
    ##
    def add_school(self):
        """Добавление новой школы"""
        # Диалоговое окно для добавления школы
        dialog = ctk.CTkToplevel(self)
        dialog.title("Добавить школу")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # Поля для ввода данных школы
        # ... реализация диалога добавления школы

    def edit_school(self, school):
        """Редактирование школы"""
        # Диалоговое окно редактирования
        pass

    def delete_school(self, school):
        """Удаление школы"""
        if messagebox.askyesno("Подтверждение", f"Удалить школу {school['name']}?"):
            # Логика удаления
            pass

    def load_values(self):
        """Загрузка значений из файла"""
        self.load_data()
        messagebox.showinfo("Успех", "Данные загружены!")

    def save_values(self):
        """Сохранение значений в файл"""
        try:
            # Сохранение common_values
            values_file = self.parent_dir.parent / 'common_values.txt'
            with open(values_file, 'w', encoding='utf-8') as f:
                f.write(f"Стоимость дня: {self.common_values['cost_eat'].get()}\n")
                f.write(f"Кол-во дней: {self.common_values['day_count'].get()}\n")
                f.write(f"Дата: {self.common_values['date'].get()}\n")
                f.write(f"Дата заключения договора: {self.common_values['date_conclusion'].get()}\n")
                f.write(f"Год: {self.common_values['year'].get()}\n")
            
            messagebox.showinfo("Успех", "Данные сохранены!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")

if __name__ == "__main__":
    app = ContractAuto_App()
    app.mainloop()