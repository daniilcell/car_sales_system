"""
Вкладка перемещения автомобилей
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import CarLocation
from utils import format_price


class TransferTab:
    """Вкладка перемещения автомобилей"""
    
    def __init__(self, parent, db, refresh_callback):
        self.db = db
        self.refresh_callback = refresh_callback
        
        self.frame = ttk.Frame(parent, padding="20")
        self.create_widgets()
        self.refresh()
    
    def create_widgets(self):
        """Создание виджетов"""
        # Верхняя панель - форма перемещения
        top_frame = ttk.LabelFrame(self.frame, text="Переместить автомобиль", padding="15")
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        form_frame = ttk.Frame(top_frame)
        form_frame.pack(fill=tk.X)
        
        # Выбор автомобиля
        ttk.Label(form_frame, text="Автомобиль:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.car_var = tk.StringVar()
        self.car_combo = ttk.Combobox(
            form_frame, 
            textvariable=self.car_var,
            width=50,
            state="readonly",
            font=('Segoe UI', 10)
        )
        self.car_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Куда перемещаем
        ttk.Label(form_frame, text="Переместить в:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.location_var = tk.StringVar()
        self.location_combo = ttk.Combobox(
            form_frame, 
            textvariable=self.location_var,
            values=[CarLocation.WAREHOUSE.value, CarLocation.DEALER_CENTER.value],
            width=20,
            state="readonly",
            font=('Segoe UI', 10)
        )
        self.location_combo.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Кнопка перемещения
        transfer_btn = ttk.Button(
            form_frame, 
            text="🚚 Переместить",
            command=self.transfer_car,
            style='Primary.TButton'
        )
        transfer_btn.grid(row=0, column=4, padx=20, pady=5)
        
        # Нижняя часть - две панели
        bottom_frame = ttk.Frame(self.frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая панель - склад
        warehouse_frame = ttk.LabelFrame(bottom_frame, text="📦 Склад", padding="10")
        warehouse_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.warehouse_tree = self.create_car_table(warehouse_frame)
        
        # Правая панель - дилерский центр
        dealer_frame = ttk.LabelFrame(bottom_frame, text="🏪 Дилерский центр", padding="10")
        dealer_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.dealer_tree = self.create_car_table(dealer_frame)
        
        # История перемещений
        history_frame = ttk.LabelFrame(self.frame, text="📋 История перемещений", padding="10")
        history_frame.pack(fill=tk.X, pady=(10, 0))
        
        columns = ("date", "car_model", "car_color", "from", "to")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=5)
        
        self.history_tree.heading("date", text="Дата")
        self.history_tree.heading("car_model", text="Модель")
        self.history_tree.heading("car_color", text="Цвет")
        self.history_tree.heading("from", text="Откуда")
        self.history_tree.heading("to", text="Куда")
        
        for col in columns:
            self.history_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_car_table(self, parent):
        """Создание таблицы автомобилей"""
        columns = ("id", "model", "color", "price")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)
        
        tree.heading("id", text="ID")
        tree.heading("model", text="Модель")
        tree.heading("color", text="Цвет")
        tree.heading("price", text="Цена")
        
        tree.column("id", width=80)
        tree.column("model", width=120)
        tree.column("color", width=100)
        tree.column("price", width=120)
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return tree
    
    def refresh(self):
        """Обновление данных"""
        # Обновление комбобокса
        cars = self.db.get_available_cars()
        car_options = [f"{c.id} - {c.model} ({c.color}) - {c.location}" for c in cars]
        self.car_combo['values'] = car_options
        
        # Обновление таблицы склада
        self.warehouse_tree.delete(*self.warehouse_tree.get_children())
        warehouse_cars = self.db.get_cars_at_location(CarLocation.WAREHOUSE.value)
        for car in warehouse_cars:
            self.warehouse_tree.insert("", tk.END, values=(
                car.id, car.model, car.color, format_price(car.price)
            ))
        
        # Обновление таблицы дилерского центра
        self.dealer_tree.delete(*self.dealer_tree.get_children())
        dealer_cars = self.db.get_cars_at_location(CarLocation.DEALER_CENTER.value)
        for car in dealer_cars:
            self.dealer_tree.insert("", tk.END, values=(
                car.id, car.model, car.color, format_price(car.price)
            ))
        
        # Обновление истории
        self.history_tree.delete(*self.history_tree.get_children())
        transfers = self.db.get_all_transfers()
        for transfer in reversed(transfers[-20:]):
            self.history_tree.insert("", tk.END, values=(
                transfer.transfer_date,
                transfer.car_model,
                transfer.car_color,
                transfer.from_location,
                transfer.to_location
            ))
    
    def transfer_car(self):
        """Перемещение автомобиля"""
        car_selection = self.car_var.get()
        new_location = self.location_var.get()
        
        if not car_selection:
            messagebox.showerror("Ошибка", "Выберите автомобиль!")
            return
        
        if not new_location:
            messagebox.showerror("Ошибка", "Выберите место назначения!")
            return
        
        car_id = car_selection.split(" - ")[0]
        car = self.db.get_car_by_id(car_id)
        
        if car.location == new_location:
            messagebox.showwarning("Внимание", "Автомобиль уже находится в этом месте!")
            return
        
        transfer = self.db.transfer_car(car_id, new_location)
        
        if transfer:
            messagebox.showinfo(
                "Успешно",
                f"Автомобиль перемещён!\n\n"
                f"Модель: {transfer.car_model}\n"
                f"Цвет: {transfer.car_color}\n"
                f"Из: {transfer.from_location}\n"
                f"В: {transfer.to_location}"
            )
            self.car_var.set("")
            self.location_var.set("")
            self.refresh_callback()
        else:
            messagebox.showerror("Ошибка", "Не удалось переместить автомобиль!")