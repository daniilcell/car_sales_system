"""
Модуль работы с базой данных (JSON-файл)
"""

import json
import os
from typing import List, Optional
from models import Car, Transfer, Sale, CarLocation, CarStatus


class Database:
    """Класс для работы с базой данных"""
    
    def __init__(self, filename: str = "data.json"):
        self.filename = filename
        self.data = {
            "cars": [],
            "transfers": [],
            "sales": []
        }
        self.load()
    
    def load(self):
        """Загрузка данных из файла"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.save()
        else:
            self.save()
    
    def save(self):
        """Сохранение данных в файл"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    # ============ Операции с автомобилями ============
    
    def add_car(self, car: Car) -> bool:
        """Добавление нового автомобиля"""
        self.data["cars"].append(car.to_dict())
        self.save()
        return True
    
    def get_all_cars(self) -> List[Car]:
        """Получение всех автомобилей"""
        return [Car.from_dict(c) for c in self.data["cars"]]
    
    def get_available_cars(self) -> List[Car]:
        """Получение доступных автомобилей"""
        return [Car.from_dict(c) for c in self.data["cars"] 
                if c["status"] != CarStatus.SOLD.value]
    
    def get_cars_at_location(self, location: str) -> List[Car]:
        """Получение автомобилей по местоположению"""
        return [Car.from_dict(c) for c in self.data["cars"] 
                if c["location"] == location and c["status"] != CarStatus.SOLD.value]
    
    def get_car_by_id(self, car_id: str) -> Optional[Car]:
        """Получение автомобиля по ID"""
        for car_data in self.data["cars"]:
            if car_data["id"] == car_id:
                return Car.from_dict(car_data)
        return None
    
    def update_car(self, car_id: str, **kwargs) -> bool:
        """Обновление данных автомобиля"""
        for i, car_data in enumerate(self.data["cars"]):
            if car_data["id"] == car_id:
                for key, value in kwargs.items():
                    if key in car_data:
                        self.data["cars"][i][key] = value
                self.save()
                return True
        return False
    
    def delete_car(self, car_id: str) -> bool:
        """Удаление автомобиля"""
        for i, car_data in enumerate(self.data["cars"]):
            if car_data["id"] == car_id:
                del self.data["cars"][i]
                self.save()
                return True
        return False
    
    # ============ Операции с перемещениями ============
    
    def add_transfer(self, transfer: Transfer) -> bool:
        """Добавление записи о перемещении"""
        self.data["transfers"].append(transfer.to_dict())
        self.save()
        return True
    
    def get_all_transfers(self) -> List[Transfer]:
        """Получение всех перемещений"""
        return [Transfer.from_dict(t) for t in self.data["transfers"]]
    
    def transfer_car(self, car_id: str, to_location: str) -> Optional[Transfer]:
        """Перемещение автомобиля"""
        car = self.get_car_by_id(car_id)
        if car and car.status != CarStatus.SOLD.value:
            transfer = Transfer(
                car_id=car.id,
                car_model=car.model,
                car_color=car.color,
                from_location=car.location,
                to_location=to_location
            )
            self.update_car(car_id, location=to_location)
            self.add_transfer(transfer)
            return transfer
        return None
    
    # ============ Операции с продажами ============
    
    def add_sale(self, sale: Sale) -> bool:
        """Добавление записи о продаже"""
        self.data["sales"].append(sale.to_dict())
        self.save()
        return True
    
    def get_all_sales(self) -> List[Sale]:
        """Получение всех продаж"""
        return [Sale.from_dict(s) for s in self.data["sales"]]
    
    def sell_car(self, car_id: str, buyer_name: str, buyer_phone: str, 
                 buyer_email: str, sale_price: float, payment_method: str) -> Optional[Sale]:
        """Продажа автомобиля"""
        car = self.get_car_by_id(car_id)
        if car and car.status != CarStatus.SOLD.value:
            sale = Sale(
                car_id=car.id,
                car_model=car.model,
                car_color=car.color,
                car_vin=car.vin,
                buyer_name=buyer_name,
                buyer_phone=buyer_phone,
                buyer_email=buyer_email,
                sale_price=sale_price,
                payment_method=payment_method
            )
            self.update_car(car_id, status=CarStatus.SOLD.value, location=CarLocation.SOLD.value)
            self.add_sale(sale)
            return sale
        return None
    
    # ============ Статистика и отчёты ============
    
    def get_statistics(self) -> dict:
        """Получение общей статистики"""
        all_cars = self.get_all_cars()
        sales = self.get_all_sales()
        
        available_cars = [c for c in all_cars if c.status != CarStatus.SOLD.value]
        warehouse_cars = [c for c in available_cars if c.location == CarLocation.WAREHOUSE.value]
        dealer_cars = [c for c in available_cars if c.location == CarLocation.DEALER_CENTER.value]
        
        total_sales = sum(s.sale_price for s in sales)
        total_inventory_value = sum(c.price for c in available_cars)
        
        return {
            "total_cars": len(all_cars),
            "available_cars": len(available_cars),
            "warehouse_cars": len(warehouse_cars),
            "dealer_cars": len(dealer_cars),
            "sold_cars": len(sales),
            "total_sales": total_sales,
            "total_inventory_value": total_inventory_value,
            "total_transfers": len(self.get_all_transfers())
        }
    
    def get_inventory_by_model(self) -> dict:
        """Получение остатков по моделям"""
        available_cars = self.get_available_cars()
        inventory = {}
        for car in available_cars:
            key = f"{car.model} ({car.color})"
            if key not in inventory:
                inventory[key] = {"count": 0, "total_price": 0, "location": car.location}
            inventory[key]["count"] += 1
            inventory[key]["total_price"] += car.price
        return inventory