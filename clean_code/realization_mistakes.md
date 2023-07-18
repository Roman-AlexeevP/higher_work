## 1.1. Методы, которые используются только в тестах

### 1

```python
def get_disallowed_defects(
    defects: List[DefectParams], grades: List[GradeParams]
) -> dict
    
```

Функция определения запрещенных дефектов для сорта присутствует только в тестах.

Решается переносом параметра valid_for_grades: Set[str] c названиями сортов во множестве, тогда дальнейшая проверка в тесте
будет тривиальна: `grade.name in defect.valid_for_grades`

## 1.2. Цепочки методов.

Таких примеров у себя не нашлось, пришлось воспользоваться общедоступным кодом)

### 1 

```python
def get_customer_address(customer):
    address = customer.get_order().get_shipping_address().get_full_address()
    return address

```

В данном случае мы должны проинкапсулировать получение полного адреса в одну функцию со стороны заказчика и со стороны класса заказа:

```python
class Customer:
    
    def get_full_address(self):
        order = self.get_order()
        full_address = order.get_full_address()
        return full_address

class Order:
    
    def get_full_address(self):
        shipping_address = self.get_shipping_address()
        return shipping_address.get_full_address()
    
customer.get_full_address() 
```

Теперь есть функции для доступа к полному адресу и зависимости спрятаны внутри реализации.

### 2 

```python
class School:
    def __init__(self, name):
        self.name = name
        self.students = []

    def add_student(self, student):
        self.students.append(student)

    def get_student_average_grade(self, student_name):
        for student in self.students:
            if student.name == student_name:
                return student.get_grades().calculate_average()

class Student:
    def __init__(self, name):
        self.name = name
        self.grades = []

    def add_grade(self, grade):
        self.grades.append(grade)

    def get_grades(self):
        return self.grades

class Grades:
    def __init__(self):
        self.grades = []

    def add_grade(self, grade):
        self.grades.append(grade)

    def calculate_average(self):
        if len(self.grades) > 0:
            total = sum(self.grades)
            average = total / len(self.grades)
            return average
        else:
            return 0
```

Здесь видна проблема в методе `get_student_average_grade` так как объекту класса School необходимо напрямую получать список оценок
 и вызывать их метод расчета.

В данном случае мы также рефакторим таким образом, чтобы инкапсулировать такие подробности в общий интерфейс:

```python

class Student:
    
    # Добавлем студенту интерфейс для метода получения его средней оценки
    def get_average_grade(self):
        return self.grades.calculate_average()
class School:
    
    # тут правим список студентов на словарь и применяем NullObject паттерн для обработки несуществуюшего имени студента
    def get_student_average_grade(self, student_name):
        return self.students.get(student_name, NullStudent).get_average_grade()
        

```

Теперь у нас более очевидный интерфейс, с ускоренным быстродействием и более удобным для расширения и улучшения кодом.

## 1.3. У метода слишком большой список параметров.

### 1

```python
def process_order(user_id, order_id, product_id, quantity, address, payment_method, discount_code, shipping_option):
    ...
```

Имея подобный код я бы  сделал два изменения:

- Сделал бы датакласс для параметров
- Разделил бы операции по функция

```python
class Order:
    def __init__(self, user_id, order_id, product_id, quantity, address, payment_method, discount_code, shipping_option):
        self.user_id = user_id
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.address = address
        self.payment_method = payment_method
        self.discount_code = discount_code
        self.shipping_option = shipping_option
    
    def calculate_total(self):
        pass
    
    def apply_discount(self):
        pass
        
    def proccess(self):
        self.calculate_total()
        self.apply_discount()
        return True
        
```

Также любой читавший про паттерны мог бы предложить сделать Builder or Manager класс, но это эффективно при необходимости
 инициализировать разные типы объектов, в то время как предложенный способ выше более универсален и не так громоздок.

## 1.4. Странные решения.

### 

## 1.5. Чрезмерный результат. Метод возвращает больше данных, чем нужно вызывающему его компоненту. 