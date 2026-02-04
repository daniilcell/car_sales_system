"""
Вкладка продаж автомобилей
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import CarLocation
from utils import format_price, parse_price, validate_phone, validate_email, PAYMENT_METHODS


class SalesTab:
    """Вкладка продаж"""
    
    def __init__(self, parent, db, refresh_callback):
        self.db = db
        self.refresh_callback = refresh_callback
        self.selected_car = None
        
        self.frame = ttk.Frame(parent, padding="20")
        self.create_widgets()
        self.refresh()
    
    def create_widgets(self):
        """Создание виджетов"""
        # Левая панель - форма продажи
        left_frame = ttk.LabelFrame(self.frame, text="💰 Оформить продажу", padding="15")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Выбор автомобиля
        ttk.Label(left_frame, text="Автомобиль:", style='SubHeader.TLabel').pack(anchor=tk.W, pady=(0, 5))
        self.car_var = tk.StringVar()
        self.car_combo = ttk.Combobox(
            left_frame, 
            textvariable=self.car_var,
            width=35,
            state="readonly",
            font=('Segoe UI', 10)
        )
        self.car_combo.pack(fill=tk.X, pady=(0, 5))
        self.car_combo.bind("<<ComboboxSelected>>", self.on_car_selected)
        
        # Информация об автомобиле
        self.car_info_label = ttk.Label(left_frame, text="", style='Info.TLabel')
        self.car_info_label.pack(anchor=tk.W, pady=(0, 15))
        
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Данные покупателя
        ttk.Label(left_frame, text="Данные покупателя:", style='SubHeader.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(left_frame, text="ФИО покупателя:").pack(anchor=tk.W, pady=(0, 5))
        self.buyer_name_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.buyer_name_var, width=37).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(left_frame, text="Телефон:").pack(anchor=tk.W, pady=(0, 5))
        self.buyer_phone_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.buyer_phone_var, width=37).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(left_frame, text="Email:").pack(anchor=tk.W, pady=(0, 5))
        self.buyer_email_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.buyer_email_var, width=37).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Детали продажи
        ttk.Label(left_frame, text="Детали продажи:", style='SubHeader.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(left_frame, text="Цена продажи (руб.):").pack(anchor=tk.W, pady=(0, 5))
        self.sale_price_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.sale_price_var, width=37).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(left_frame, text="Способ оплаты:").pack(anchor=tk.W, pady=(0, 5))
        self.payment_var = tk.StringVar(value=PAYMENT_METHODS[0])
        ttk.Combobox(
            left_frame, 
            textvariable=self.payment_var,
            values=PAYMENT_METHODS,
            state="readonly",
            width=35
        ).pack(fill=tk.X, pady=(0, 15))
        
        # Кнопка продажи
        sell_btn = ttk.Button(
            left_frame, 
            text="✅ Оформить продажу",
            command=self.sell_car,
            style='Primary.TButton'
        )
        sell_btn.pack(fill=tk.X, pady=(10, 5))
        
        # Кнопка очистки
        clear_btn = ttk.Button(
            left_frame, 
            text="🗑️ Очистить форму",
            command=self.clear_form
        )
        clear_btn.pack(fill=tk.X)
        
        # Правая панель - история продаж
        right_frame = ttk.LabelFrame(self.frame, text="📋 История продаж", padding="15")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Таблица продаж
        columns = ("date", "model", "color", "buyer", "price", "payment")
        self.sales_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=20)
        
        self.sales_tree.heading("date", text="Дата")
        self.sales_tree.heading("model", text="Модель")
        self.sales_tree.heading("color", text="Цвет")
        self.sales_tree.heading("buyer", text="Покупатель")
        self.sales_tree.heading("price", text="Цена")
        self.sales_tree.heading("payment", text="Способ оплаты")
        
        self.sales_tree.column("date", width=120)
        self.sales_tree.column("model", width=120)
        self.sales_tree.column("color", width=80)
        self.sales_tree.column("buyer", width=180)
        self.sales_tree.column("price", width=120)
        self.sales_tree.column("payment", width=120)
        
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scrollbar.set)
        
        self.sales_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Двойной клик для просмотра деталей
        self.sales_tree.bind("<Double-1>", self.show_sale_details)
    
    def on_car_selected(self, event=None):
        """Обработка выбора автомобиля"""
        car_selection = self.car_var.get()
        if car_selection:
            car_id = car_selection.split(" - ")[0]
            car = self.db.get_car_by_id(car_id)
            if car:
                self.selected_car = car
                self.car_info_label.config(
                    text=f"VIN: {car.vin}\nЦена: {format_price(car.price)}\nЛокация: {car.location}"
                )
                self.sale_price_var.set(str(int(car.price)))
    
    def refresh(self):
        """Обновление данных"""
        # Обновление комбобокса
        cars = self.db.get_available_cars()
        car_options = [f"{c.id} - {c.model} ({c.color})" for c in cars]
        self.car_combo['values'] = car_options
        
        # Обновление истории продаж
        self.sales_tree.delete(*self.sales_tree.get_children())
        sales = self.db.get_all_sales()
        for sale in reversed(sales):
            self.sales_tree.insert("", tk.END, values=(
                sale.sale_date,
                sale.car_model,
                sale.car_color,
                sale.buyer_name,
                format_price(sale.sale_price),
                sale.payment_method
            ), tags=(sale.id,))
    
    def sell_car(self):
        """Оформление продажи"""
        if not self.selected_car:
            messagebox.showerror("Ошибка", "Выберите автомобиль!")
            return
        
        buyer_name = self.buyer_name_var.get().strip()
        buyer_phone = self.buyer_phone_var.get().strip()
        buyer_email = self.buyer_email_var.get().strip()
        price_str = self.sale_price_var.get().strip()
        payment_method = self.payment_var.get()
        
        # Валидация
        if not buyer_name:
            messagebox.showerror("Ошибка", "Укажите ФИО покупателя!")
            return
        
        if not buyer_phone:
            messagebox.showerror("Ошибка", "Укажите телефон покупателя!")
            return
        
        if not validate_phone(buyer_phone):
            messagebox.showerror("Ошибка", "Некорректный номер телефона!")
            return
        
        if buyer_email and not validate_email(buyer_email):
            messagebox.showerror("Ошибка", "Некорректный email!")
            return
        
        sale_price = parse_price(price_str)
        if sale_price is None or sale_price <= 0:
            messagebox.showerror("Ошибка", "Укажите корректную цену продажи!")
            return
        
        # Подтверждение
        confirm = messagebox.askyesno(
            "Подтверждение продажи",
            f"Оформить продажу?\n\n"
            f"Автомобиль: {self.selected_car.model} ({self.selected_car.color})\n"
            f"VIN: {self.selected_car.vin}\n"
            f"Покупатель: {buyer_name}\n"
            f"Цена: {format_price(sale_price)}\n"
            f"Способ оплаты: {payment_method}"
        )
        
        if confirm:
            sale = self.db.sell_car(
                car_id=self.selected_car.id,
                buyer_name=buyer_name,
                buyer_phone=buyer_phone,
                buyer_email=buyer_email or "",
                sale_price=sale_price,
                payment_method=payment_method
            )
            
            if sale:
                messagebox.showinfo(
                    "Продажа оформлена!",
                    f"✅ Автомобиль успешно продан!\n\n"
                    f"Номер сделки: {sale.id}\n"
                    f"Модель: {sale.car_model}\n"
                    f"Покупатель: {sale.buyer_name}\n"
                    f"Сумма: {format_price(sale.sale_price)}"
                )
                self.clear_form()
                self.refresh_callback()
            else:
                messagebox.showerror("Ошибка", "Не удалось оформить продажу!")
    
    def clear_form(self):
        """Очистка формы"""
        self.car_var.set("")
        self.buyer_name_var.set("")
        self.buyer_phone_var.set("")
        self.buyer_email_var.set("")
        self.sale_price_var.set("")
        self.payment_var.set(PAYMENT_METHODS[0])
        self.car_info_label.config(text="")
        self.selected_car = None
    
    def show_sale_details(self, event):
        """Показ деталей продажи"""
        selected = self.sales_tree.selection()
        if selected:
            item = self.sales_tree.item(selected[0])
            values = item["values"]
            sale_id = item["tags"][0] if item["tags"] else ""
            
            # Находим полную информацию о продаже
            sales = self.db.get_all_sales()
            sale = next((s for s in sales if s.id == sale_id), None)
            
            if sale:
                details = (
                    f"📋 Детали продажи #{sale.id}\n\n"
                    f"{'='*40}\n\n"
                    f"🚗 АВТОМОБИЛЬ:\n"
                    f"   Модель: {sale.car_model}\n"
                    f"   Цвет: {sale.car_color}\n"
                    f"   VIN: {sale.car_vin}\n\n"
                    f"👤 ПОКУПАТЕЛЬ:\n"
                    f"   ФИО: {sale.buyer_name}\n"
                    f"   Телефон: {sale.buyer_phone}\n"
                    f"   Email: {sale.buyer_email or 'Не указан'}\n\n"
                    f"💰 ОПЛАТА:\n"
                    f"   Сумма: {format_price(sale.sale_price)}\n"
                    f"   Способ: {sale.payment_method}\n"
                    f"   Дата: {sale.sale_date}"
                )
                messagebox.showinfo("Детали продажи", details)