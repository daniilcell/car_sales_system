"""
Вкладка отчётов
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import format_price


class ReportsTab:
    """Вкладка отчётов"""
    
    def __init__(self, parent, db):
        self.db = db
        
        self.frame = ttk.Frame(parent, padding="20")
        self.create_widgets()
        self.refresh()
    
    def create_widgets(self):
        """Создание виджетов"""
        # Верхняя панель - статистика
        stats_frame = ttk.LabelFrame(self.frame, text="📊 Общая статистика", padding="15")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Карточки статистики
        cards_frame = ttk.Frame(stats_frame)
        cards_frame.pack(fill=tk.X)
        
        self.stat_cards = {}
        
        card_configs = [
            ("total_cars", "📦 Всего автомобилей", "#3498db"),
            ("available_cars", "✅ Доступно", "#2ecc71"),
            ("warehouse_cars", "🏭 На складе", "#9b59b6"),
            ("dealer_cars", "🏪 В дилерских центрах", "#e67e22"),
            ("sold_cars", "💰 Продано", "#e74c3c"),
            ("total_sales", "💵 Сумма продаж", "#1abc9c"),
        ]
        
        for i, (key, title, color) in enumerate(card_configs):
            card = self.create_stat_card(cards_frame, title, "0", color)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            self.stat_cards[key] = card
            cards_frame.columnconfigure(i, weight=1)
        
        # Средняя часть - две панели
        middle_frame = ttk.Frame(self.frame)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Остатки по моделям
        inventory_frame = ttk.LabelFrame(middle_frame, text="📋 Остатки на складе", padding="10")
        inventory_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        columns = ("model", "count", "total_price", "location")
        self.inventory_tree = ttk.Treeview(inventory_frame, columns=columns, show="headings", height=12)
        
        self.inventory_tree.heading("model", text="Модель (Цвет)")
        self.inventory_tree.heading("count", text="Количество")
        self.inventory_tree.heading("total_price", text="Общая стоимость")
        self.inventory_tree.heading("location", text="Местоположение")
        
        for col in columns:
            self.inventory_tree.column(col, width=150)
        
        scrollbar1 = ttk.Scrollbar(inventory_frame, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar1.set)
        
        self.inventory_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar1.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Последние продажи
        sales_frame = ttk.LabelFrame(middle_frame, text="💰 Последние продажи", padding="10")
        sales_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        columns = ("date", "model", "buyer", "price")
        self.recent_sales_tree = ttk.Treeview(sales_frame, columns=columns, show="headings", height=12)
        
        self.recent_sales_tree.heading("date", text="Дата")
        self.recent_sales_tree.heading("model", text="Модель")
        self.recent_sales_tree.heading("buyer", text="Покупатель")
        self.recent_sales_tree.heading("price", text="Цена")
        
        for col in columns:
            self.recent_sales_tree.column(col, width=120)
        
        scrollbar2 = ttk.Scrollbar(sales_frame, orient=tk.VERTICAL, command=self.recent_sales_tree.yview)
        self.recent_sales_tree.configure(yscrollcommand=scrollbar2.set)
        
        self.recent_sales_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Нижняя панель - кнопки экспорта
        export_frame = ttk.LabelFrame(self.frame, text="📤 Экспорт отчётов", padding="10")
        export_frame.pack(fill=tk.X)
        
        btn_frame = ttk.Frame(export_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(
            btn_frame, 
            text="📄 Отчёт о продажах (TXT)",
            command=self.export_sales_report
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="📦 Отчёт об остатках (TXT)",
            command=self.export_inventory_report
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="📊 Полный отчёт (TXT)",
            command=self.export_full_report
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="🔄 Обновить",
            command=self.refresh,
            style='Primary.TButton'
        ).pack(side=tk.RIGHT, padx=5)
    
    def create_stat_card(self, parent, title, value, color):
        """Создание карточки статистики"""
        card = ttk.Frame(parent, relief="solid", borderwidth=1)
        
        title_label = ttk.Label(card, text=title, font=('Segoe UI', 9))
        title_label.pack(pady=(10, 5))
        
        value_label = ttk.Label(card, text=value, font=('Segoe UI', 18, 'bold'))
        value_label.pack(pady=(0, 10))
        
        card.value_label = value_label
        return card
    
    def refresh(self):
        """Обновление отчётов"""
        stats = self.db.get_statistics()
        
        # Обновление карточек
        self.stat_cards["total_cars"].value_label.config(text=str(stats["total_cars"]))
        self.stat_cards["available_cars"].value_label.config(text=str(stats["available_cars"]))
        self.stat_cards["warehouse_cars"].value_label.config(text=str(stats["warehouse_cars"]))
        self.stat_cards["dealer_cars"].value_label.config(text=str(stats["dealer_cars"]))
        self.stat_cards["sold_cars"].value_label.config(text=str(stats["sold_cars"]))
        self.stat_cards["total_sales"].value_label.config(text=format_price(stats["total_sales"]))
        
        # Обновление остатков
        self.inventory_tree.delete(*self.inventory_tree.get_children())
        inventory = self.db.get_inventory_by_model()
        for model, data in inventory.items():
            self.inventory_tree.insert("", tk.END, values=(
                model,
                data["count"],
                format_price(data["total_price"]),
                data["location"]
            ))
        
        # Обновление последних продаж
        self.recent_sales_tree.delete(*self.recent_sales_tree.get_children())
        sales = self.db.get_all_sales()
        for sale in reversed(sales[-10:]):
            self.recent_sales_tree.insert("", tk.END, values=(
                sale.sale_date,
                sale.car_model,
                sale.buyer_name,
                format_price(sale.sale_price)
            ))
    
    def export_sales_report(self):
        """Экспорт отчёта о продажах"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialname=f"sales_report_{datetime.now().strftime('%Y%m%d')}.txt"
        )
        
        if filename:
            sales = self.db.get_all_sales()
            stats = self.db.get_statistics()
            
            report = []
            report.append("=" * 60)
            report.append("         ОТЧЁТ О ПРОДАЖАХ АВТОМОБИЛЕЙ")
            report.append(f"         Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            report.append("=" * 60)
            report.append("")
            report.append(f"Продано автомобилей: {stats['sold_cars']}")
            report.append(f"Общая сумма продаж: {format_price(stats['total_sales'])}")
            report.append("")
            report.append("-" * 60)
            report.append("ДЕТАЛИЗАЦИЯ ПРОДАЖ:")
            report.append("-" * 60)
            
            for sale in sales:
                report.append(f"\nДата: {sale.sale_date}")
                report.append(f"Покупатель: {sale.buyer_name}")
                report.append(f"Модель автомобиля: {sale.car_model}")
                report.append(f"Цвет автомобиля: {sale.car_color}")
                report.append(f"VIN: {sale.car_vin}")
                report.append(f"Цена автомобиля: {format_price(sale.sale_price)}")
                report.append(f"Способ оплаты: {sale.payment_method}")
                report.append("-" * 40)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report))
            
            messagebox.showinfo("Успешно", f"Отчёт сохранён:\n{filename}")
    
    def export_inventory_report(self):
        """Экспорт отчёта об остатках"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialname=f"inventory_report_{datetime.now().strftime('%Y%m%d')}.txt"
        )
        
        if filename:
            stats = self.db.get_statistics()
            inventory = self.db.get_inventory_by_model()
            
            report = []
            report.append("=" * 60)
            report.append("         ОТЧЁТ ОБ ОСТАТКАХ НА СКЛАДЕ")
            report.append(f"         Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            report.append("=" * 60)
            report.append("")
            report.append(f"Всего автомобилей в наличии: {stats['available_cars']}")
            report.append(f"На складе: {stats['warehouse_cars']}")
            report.append(f"В дилерских центрах: {stats['dealer_cars']}")
            report.append(f"Общая стоимость остатков: {format_price(stats['total_inventory_value'])}")
            report.append("")
            report.append("-" * 60)
            report.append("ОСТАТКИ ПО МОДЕЛЯМ:")
            report.append("-" * 60)
            
            for model, data in inventory.items():
                report.append(f"\nМодель автомобиля: {model}")
                report.append(f"Количество: {data['count']}")
                report.append(f"Общая стоимость: {format_price(data['total_price'])}")
                report.append(f"Местоположение: {data['location']}")
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report))
            
            messagebox.showinfo("Успешно", f"Отчёт сохранён:\n{filename}")
    
    def export_full_report(self):
        """Экспорт полного отчёта"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialname=f"full_report_{datetime.now().strftime('%Y%m%d')}.txt"
        )
        
        if filename:
            stats = self.db.get_statistics()
            inventory = self.db.get_inventory_by_model()
            sales = self.db.get_all_sales()
            
            report = []
            report.append("=" * 70)
            report.append("              ПОЛНЫЙ ОТЧЁТ СИСТЕМЫ УПРАВЛЕНИЯ")
            report.append("                    ПРОДАЖАМИ АВТОМОБИЛЕЙ")
            report.append(f"           Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            report.append("=" * 70)
            
            # Общая статистика
            report.append("\n" + "=" * 70)
            report.append("                       ОБЩАЯ СТАТИСТИКА")
            report.append("=" * 70)
            report.append(f"Всего автомобилей в системе: {stats['total_cars']}")
            report.append(f"Доступно для продажи: {stats['available_cars']}")
            report.append(f"На складе: {stats['warehouse_cars']}")
            report.append(f"В дилерских центрах: {stats['dealer_cars']}")
            report.append(f"Продано: {stats['sold_cars']}")
            report.append(f"Общая сумма продаж: {format_price(stats['total_sales'])}")
            report.append(f"Стоимость остатков: {format_price(stats['total_inventory_value'])}")
            report.append(f"Количество перемещений: {stats['total_transfers']}")
            
            # Остатки
            report.append("\n" + "=" * 70)
            report.append("                      ОСТАТКИ НА СКЛАДЕ")
            report.append("=" * 70)
            for model, data in inventory.items():
                report.append(f"  {model}: {data['count']} шт. - {format_price(data['total_price'])}")
            
            # Продажи
            report.append("\n" + "=" * 70)
            report.append("                        ИНФОРМАЦИЯ О ПРОДАЖАХ")
            report.append("=" * 70)
            for sale in sales:
                report.append(f"\n  [{sale.sale_date}] {sale.car_model} ({sale.car_color})")
                report.append(f"    Покупатель: {sale.buyer_name}")
                report.append(f"    Цена автомобиля: {format_price(sale.sale_price)}")
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report))
            
            messagebox.showinfo("Успешно", f"Полный отчёт сохранён:\n{filename}")