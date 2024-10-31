from dataclasses import dataclass
from enum import Enum
from typing import Union


@dataclass
class Good:
    code: str
    name: str
    price: float
    status: str


class BaseEnum2(Enum):
    """
    Розширення класу Enum, яке дозволяє тримати в собі допоміжні властивості обраного елементу
    Може ініціюватить яз за base_name так і за base_value
    Приклад:
        class MySubProcess(ProcessInfo):
            INITIALIZATION = ("INITIALIZATION", "Ініціалізація зміни на ПОН")
            REQUEST_DATA_IN_ATKO = ("REQUEST_DATA_IN_ATKO", "Запит даних у АТКО")

        1.
        a = MyClass.INITIALIZATION
        a.name             ->  'INITIALIZATION'
        str(a)             ->  'INITIALIZATION'
        str(a.name)        ->  'INITIALIZATION'
        str(a.base_name)   ->  'INITIALIZATION'
        str(a.value)       ->  'Ініціалізація зміни на ПОН'
        str(a.base_value)  ->  'Ініціалізація зміни на ПОН'

        2.
        y = MyClass('request-data-in-atko')
        y = MyClass('REQUEST_DATA_IN_ATKO')
    """

    def __init__(self, base_name: str, base_value: Union[str, int, dict]):
        self.base_name = base_name
        self.base_value = base_value

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}.{self.base_name}>"

    def __new__(cls, base_name: str, base_value: Union[str, int, dict]):
        obj = object.__new__(cls)
        # яке з властивостей є дефолтним
        obj._value_ = base_value
        # зберігаємо за якими властивостями обєкт може ініціюватить (base_name, base_value)
        cls._value2member_map_[base_name] = obj
        if isinstance(base_value, str) or isinstance(base_value, int):
            cls._value2member_map_[base_value] = obj
        return obj




class GoodStatus(BaseEnum2):
    AVAILABLE = ("AVAILABLE", "Dostępny")
    RESERVED = ("RESERVED", "Rezerwacja")
    ORDER = ("ORDER", "Wielopak")
