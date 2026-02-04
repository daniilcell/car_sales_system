"""
Модели данных для системы управления продажами автомобилей
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid


class CarLocation(Enum):
    """Местоположение автомобиля"""
    WAREHOUSE = "Склад"
    DEALER_CENTER = "Дилерский центр"
    SOLD = "Продан"


class CarStatus(Enum):
    """Статус автомобиля"""
    AVAILABLE = "Доступен"
    RESERVED = "Зарезервирован"
    SOLD = "Продан"


@dataclass
class Car:
    """Модель автомобиля"""
    model: str
    color: str
    price: float
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    location: str = CarLocation.WAREHOUSE.value
    status: str = CarStatus.AVAILABLE.value
    arrival_date: str = field(default_factory=lambda: datetime.now().strftime("%d.%m.%Y %H:%M"))
    vin: str = field(default_factory=lambda: f"VIN{uuid.uuid4().hex[:14].upper()}")
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Car':
        return cls(**data)


@dataclass
class Transfer:
    """Модель перемещения автомобиля"""
    car_id: str
    car_model: str
    car_color: str
    from_location: str
    to_location: str
    transfer_date: str = field(default_factory=lambda: datetime.now().strftime("%d.%m.%Y %H:%M"))
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Transfer':
        return cls(**data)


@dataclass
class Sale:
    """Модель продажи"""
    car_id: str
    car_model: str
    car_color: str
    car_vin: str
    buyer_name: str
    buyer_phone: str
    buyer_email: str
    sale_price: float
    sale_date: str = field(default_factory=lambda: datetime.now().strftime("%d.%m.%Y %H:%M"))
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    payment_method: str = "Наличные"
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Sale':
        return cls(**data)