"""
Главное окно приложения
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database
from .arrival_tab import ArrivalTab
from .transfer_tab import TransferTab
from .sales_tab import SalesTab
from .reports_tab import ReportsTab


class MainWindow:
    """Главное окно приложения"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚗 Система управления продажами автомобилей")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Центрирование окна
        self.center_window()
        
        # Инициализация базы данных
        self.db = Database()
        
        # Настройка стилей
        self.setup_styles()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обработка закрытия
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = 1200
        height = 800
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_styles(self):
        """Настройка стилей"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Общие стили
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10), padding=5)
        style.configure('TEntry', font=('Segoe UI', 10))
        
        # Стили для вкладок
        style.configure('TNotebook', background='#f0f0f0')
        style.configure('TNotebook.Tab', font=('Segoe UI', 11, 'bold'), padding=[20, 10])
        
        # Стили для заголовков
        style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#2c3e50')
        style.configure('SubHeader.TLabel', font=('Segoe UI', 12, 'bold'), foreground='#34495e')
        style.configure('Info.TLabel', font=('Segoe UI', 10), foreground='#7f8c8d')
        
        # Стили для кнопок
        style.configure('Primary.TButton', font=('Segoe UI', 11, 'bold'))
        style.configure('Success.TButton', font=('Segoe UI', 10))
        style.configure('Danger.TButton', font=('Segoe UI', 10))
        
        # Стили для Treeview
        style.configure('Treeview', font=('Segoe UI', 10), rowheight=30)
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
    
    def create_widgets(self):
        """Создание виджетов"""
        # Главный контейнер
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame, 
            text="🚗 Система управления продажами автомобилей",
            style='Header.TLabel'
        )
        title_label.pack(side=tk.LEFT)
        
        # Кнопка обновления
        refresh_btn = ttk.Button(
            header_frame, 
            text="🔄 Обновить",
            command=self.refresh_all,
            style='Primary.TButton'
        )
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Создание вкладок
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка поступления
        self.arrival_tab = ArrivalTab(self.notebook, self.db, self.refresh_all)
        self.notebook.add(self.arrival_tab.frame, text="📦 Поступление")
        
        # Вкладка перемещения
        self.transfer_tab = TransferTab(self.notebook, self.db, self.refresh_all)
        self.notebook.add(self.transfer_tab.frame, text="🚚 Перемещение")
        
        # Вкладка продаж
        self.sales_tab = SalesTab(self.notebook, self.db, self.refresh_all)
        self.notebook.add(self.sales_tab.frame, text="💰 Продажи")
        
        # Вкладка отчётов
        self.reports_tab = ReportsTab(self.notebook, self.db)
        self.notebook.add(self.reports_tab.frame, text="📊 Отчёты")
        
        # Статусная строка
        self.create_status_bar(main_container)
    
    def create_status_bar(self, parent):
        """Создание статусной строки"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(
            status_frame, 
            text="Готово к работе",
            style='Info.TLabel'
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Статистика
        self.stats_label = ttk.Label(status_frame, text="", style='Info.TLabel')
        self.stats_label.pack(side=tk.RIGHT)
        
        self.update_stats()
    
    def update_stats(self):
        """Обновление статистики в статусной строке"""
        stats = self.db.get_statistics()
        text = (f"📦 На складе: {stats['warehouse_cars']} | "
                f"🏪 В дилерских центрах: {stats['dealer_cars']} | "
                f"💰 Продано: {stats['sold_cars']}")
        self.stats_label.config(text=text)
    
    def refresh_all(self):
        """Обновление всех вкладок"""
        self.arrival_tab.refresh()
        self.transfer_tab.refresh()
        self.sales_tab.refresh()
        self.reports_tab.refresh()
        self.update_stats()
        self.status_label.config(text="Данные обновлены")
    
    def on_closing(self):
        """Обработка закрытия окна"""
        if messagebox.askokcancel("Выход", "Вы действительно хотите выйти?"):
            self.root.destroy()
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()