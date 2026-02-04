"""
Вкладка поступления автомобилей
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Car
from utils import CAR_MODELS, CAR_COLORS, format_price, parse_price


class ArrivalTab:
    """Вкладка поступления автомобилей"""
    
    def __init__(self, parent, db, refresh_callback):
        self.db = db
        self.refresh_callback = refresh_callback
        
        self.frame = ttk.Frame(parent, padding="20")
        self.create_widgets()
        self.refresh()
    
    def create_widgets(self):
        """Создание виджетов"""
        # Левая панель - форма добавления
        left_frame = ttk.LabelFrame(self.frame, text="Добавить новый автомобиль", padding="15")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Модель
        ttk.Label(left_frame, text="Модель автомобиля:").pack(anchor=tk.W, pady=(0, 5))
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(
            left_frame, 
            textvariable=self.model_var, 
            values=CAR_MODELS,
            width=30,
            font=('Segoe UI', 10)
        )
        self.model_combo.pack(fill=tk.X, pady=(0, 15))
        
        # Цвет
        ttk.Label(left_frame, text="Цвет автомобиля:").pack(anchor=tk.W, pady=(0, 5))
        self.color_var = tk.StringVar()
        self.color_combo = ttk.Combobox(
            left_frame, 
            textvariable=self.color_var, 
            values=CAR_COLORS,
            width=30,
            font=('Segoe UI', 10)
        )
        self.color_combo.pack(fill=tk.X, pady=(0, 15))
        
        # Цена
        ttk.Label(left_frame, text="Цена автомобиля (руб.):").pack(anchor=tk.W, pady=(0, 5))
        self.price_var = tk.StringVar()
        self.price_entry = ttk.Entry(
            left_frame, 
            textvariable=self.price_var,
            width=32,
            font=('Segoe UI', 10)
        )
        self.price_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Количество
        ttk.Label(left_frame, text="Количество:").pack(anchor=tk.W, pady=(0, 5))
        self.quantity_var = tk.StringVar(value="1")
        self.quantity_spin = ttk.Spinbox(
            left_frame, 
            from_=1, 
            to=100, 
            textvariable=self.quantity_var,
            width=30,
            font=('Segoe UI', 10)
        )
        self.quantity_spin.pack(fill=tk.X, pady=(0, 20))
        
        # Кнопка добавления
        add_btn = ttk.Button(
            left_frame, 
            text="➕ Добавить на склад",
            command=self.add_car,
            style='Primary.TButton'
        )
        add_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Кнопка очистки
        clear_btn = ttk.Button(
            left_frame, 
            text="🗑️ Очистить форму",
            command=self.clear_form
        )
        clear_btn.pack(fill=tk.X)
        
        # Правая панель - список автомобилей на складе
        right_frame = ttk.LabelFrame(self.frame, text="Автомобили на складе", padding="15")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Поиск
        search_frame = ttk.Frame(right_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="🔍 Поиск:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_cars())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Таблица автомобилей
        columns = ("id", "model", "color", "price", "location", "date")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("model", text="Модель")
        self.tree.heading("color", text="Цвет")
        self.tree.heading("price", text="Цена")
        self.tree.heading("location", text="Местоположение")
        self.tree.heading("date", text="Дата поступления")
        
        self.tree.column("id", width=80)
        self.tree.column("model", width=150)
        self.tree.column("color", width=100)
        self.tree.column("price", width=120)
        self.tree.column("location", width=130)
        self.tree.column("date", width=140)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Контекстное меню
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="🗑️ Удалить", command=self.delete_selected)
        self.tree.bind("<Button-3>", self.show_context_menu)
    
    def add_car(self):
        """Добавление автомобиля"""
        model = self.model_var.get().strip()
        color = self.color_var.get().strip()
        price_str = self.price_var.get().strip()
        
        if not model:
            messagebox.showerror("Ошибка", "Укажите модель автомобиля!")
            return
        
        if not color:
            messagebox.showerror("Ошибка", "Укажите цвет автомобиля!")
            return
        
        price = parse_price(price_str)
        if price is None or price <= 0:
            messagebox.showerror("Ошибка", "Укажите корректную цену!")
            return
        
        try:
            quantity = int(self.quantity_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Укажите корректное количество!")
            return
        
        # Добавляем указанное количество автомобилей
        for _ in range(quantity):
            car = Car(model=model, color=color, price=price)
            self.db.add_car(car)
        
        messagebox.showinfo(
            "Успешно", 
            f"Добавлено автомобилей: {quantity}\n"
            f"Модель: {model}\n"
            f"Цвет: {color}\n"
            f"Цена: {format_price(price)}"
        )
        
        self.clear_form()
        self.refresh_callback()
    
    def clear_form(self):
        """Очистка формы"""
        self.model_var.set("")
        self.color_var.set("")
        self.price_var.set("")
        self.quantity_var.set("1")
    
    def refresh(self):
        """Обновление списка автомобилей"""
        self.tree.delete(*self.tree.get_children())
        cars = self.db.get_available_cars()
        
        for car in cars:
            self.tree.insert("", tk.END, values=(
                car.id,
                car.model,
                car.color,
                format_price(car.price),
                car.location,
                car.arrival_date
            ))
    
    def filter_cars(self):
        """Фильтрация автомобилей"""
        search_text = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        cars = self.db.get_available_cars()
        
        for car in cars:
            if (search_text in car.model.lower() or 
                search_text in car.color.lower() or
                search_text in car.id.lower()):
                self.tree.insert("", tk.END, values=(
                    car.id,
                    car.model,
                    car.color,
                    format_price(car.price),
                    car.location,
                    car.arrival_date
                ))
    
    def show_context_menu(self, event):
        """Показ контекстного меню"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def delete_selected(self):
        """Удаление выбранного автомобиля"""
        selected = self.tree.selection()
        if not selected:
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранный автомобиль?"):
            car_id = self.tree.item(selected[0])["values"][0]
            self.db.delete_car(car_id)
            self.refresh_callback()