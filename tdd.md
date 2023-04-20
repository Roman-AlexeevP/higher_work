Ссылка на репозиторий: https://github.com/Roman-AlexeevP/money_analizer
Хранение и анализ домашних финансов
Главные сущности:

Трата:
- Кол-во денег
- Когда и во сколько
- Категория трат

В данном примере репозитория видно, что сделан упор конкретные параметры сущности, хотя они не согласованы со спецификацией

@dataclasses.dataclass  
class Expense:  
  
    money: Union[int, float]  
    created_at: datetime  
    category: str
 
сущность и ее создание уже дает простор для ошибок, которые как раз-таки вытекают из спецификации.
Есть два теста: чтение из файла и БД и там и там проверяется корректность механизмов чтения объектов, но не свойства нашей сущности.
А свойства такие:

- Кол-во денег, очевидно не может быть отрицательным, пустым 
- Дата траты, очевидно не может быть из будущего, так как система работает только с уже случившимися тратами
- Категория трат должна быть не пустой строкой, а желательно при отсутствии выставляться в дефолтную категорию
Из этого вытекают подобные правки к коду и тестам:

```
  
import dataclasses  
from datetime import datetime  
from typing import Union, Dict  
  
  
class Validations:  
    def __post_init__(self):  
        for name, field in self.__dataclass_fields__.items():  
            if (method := getattr(self, f"validate_{name}", None)):  
                setattr(self, name, method(getattr(self, name), field=field))  
  
  
@dataclasses.dataclass  
class Expense(Validations):  
    DEFAULT_CATEGORY = "Другое"  
  
    money: Union[int, float] = 0  
    created_at: datetime = datetime.now()  
    category: str = DEFAULT_CATEGORY  
  
    def validate_money(self, value, **_):  
        if not isinstance(value, (float, int)):  
            raise ValueError("Money must be number")  
        if not validate_positive_number(value):  
            raise ValueError("Money must be positive number")  
        return value  
  
    def validate_created_at(self, value, **_):  
        if not validate_date_in_past(value):  
            raise ValueError("Expense must be done in the past")  
        return value  
  
  
class InvalidExpense(Expense):  
  
    def __init__(self):  
        super().__init__(money=None, created_at=None, category=None)  
  
  
def validate_non_empty(value):  
    return value != "" and value is not None  
  
  
def validate_positive_number(value):  
    return value > 0  
  
  
def validate_date_in_past(value):  
    now = datetime.now()  
    return now > value  
  
  
class ExpenseFabric:  
  
    @classmethod  
    def create_expense(cls, raw_data):  
        try:  
            expense = Expense(*raw_data)  
        except ValueError:  
            expense = InvalidExpense()  
        return expense
```

Добавляем нулевой объект для траты и валидацию, чтобы проверять корректность объекта в системе в принципе, а не его наличие, таким образом  тесты уже проверяет наличие корректных сущностей, а не в принципе объектов.
Фабрика создает различные варианты сущностей и мы можем проверять фильтром уже в любом обработчике внешних данных,  например:
```
valid_expenses = list(filter(lambda x: isinstance(x, Expense), expenses))
```

Тем самым не добавляя в рантайм невалидные объекты.
