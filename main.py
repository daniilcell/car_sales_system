"""
Система управления продажами автомобилей
Главный файл приложения
"""

import sys
import os

# Добавляем текущую директорию в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow


def main():
    """Главная функция"""
    print("🚗 Запуск системы управления продажами автомобилей...")
    
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()