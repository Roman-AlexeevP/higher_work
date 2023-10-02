# 1 пример

Было:

```python

@dataclass
class Person:
    name: str
    age: int
    phone: str




def get_persons_list():
    persons = list(db.get_persons())
    return sorted(persons, key=lambda person: person.age)

def process_persons_by_age(persons):
    persons = sorted(persons, key=lambda person: person.age)
    do_something(persons)

```

стало:

```python

@dataclass
class Person:
    name: str
    age: int
    phone: str


@dataclass
class SortedPersonByAgeCollection:

    persons: List[Person]
    
    def __post_init__(self):
        self.persons = sorted(persons, key=lambda person: person.age)

def get_persons_list():
    persons = PersonCollection(db.get_persons())
    return persons

def process_persons_by_age(persons):
    do_something(persons)

```

В данном примере, так как мы не уверены, что коллекция отсортирована везде сортируем и дублируем код, рискуя
 в какой-то момент это упустить. Для исправления этой ошибки, мы создаем кастомную коллекции с инвариантом в виде
отсортированного списка сущностей, что позволяет везде пользоваться конкретной коллекцией без уточнений и ошибок.


# пример 2

Было:
```python

def test_config(django_settings, tmp_path):
    django_settings.HOST_NAME = "localhost"
    django_settings.ALLOWED_HOSTS = ["testserver", "localhost"]
    assert not django_settings.SECURE_SSL_REDIRECT, "Should be False for testing"  
    django_settings.MEDIA_ROOT = tmp_path


```

Стало:
`test_settings.py`
```python
HOST_NAME = "localhost"
ALLOWED_HOSTS = ["testserver", "localhost"]
SECURE_SSL_REDIRECT = False
MEDIA_ROOT = tmp_path()
```

Вместо проверки валидности переставленных параметров для тестирования, необходимо создать отдельный файл
 настроек для тестов и там явно указать все изменившиеся поля, тогда необходимость в проверке отпадет. 

# пример 3 

было:

```python

def get_icon(self, obj):
    try:
        icon = obj.name.icon
        if not icon or (len(icon) == 0):
            return None
        http_host = get_content_host()
        url = "http://{0}{1}{2}".format(http_host, settings.ICONS_URL, icon)
        return url
    except Exception:
        logger.critical("No local link for icon %d", obj.id, exc_info=1)
        return ""


```

стало:

```python

class MyObject:
        
    @property
    def icon(self):
        return self.icon or DEFAULT_ICON_LINK

def get_icon(self, obj):
    icon = obj.name.icon
    http_host = get_content_host()
    url = "http://{0}{1}{2}".format(http_host, settings.ICONS_URL, icon)
    return url
```

Сокращаем область try_except и выносим его в функцию get_content_host(), а классу, чья ссылка на иконку должна
быть получена загружаем и выставляем дефолтное изображения для случаев отсутствующего изображения.

# Пример 4

было:
```python

class Screen:
    def __init__(self, size, size_type):
        self.size = size
        self.size_type = size_type
        
def compare_screens(screen1, screen2):
    if screen1.size_type == screen2.size_type:
        return screen1.size > screen2.size_type
    else:
        raise ValueError()
    


```

стало:

```python
class Screen:
    def __init__(self, size, size_type):
        self.size = size
        self.size_type = size_type
    
    def compare(self, another_screen):
        new_size = self.convert_size(another_screen)
        return self.size > another_screen.size
```


В данном случае вся логика ушла в класс Screen, который отвечает за достоверность сравнения по одинаковой размерности и
лишний раз внутренее состояние класса не достается из лишних функций.

# Пример 5

было:
```python

def post_purchase(request):
 
    if request.method != 'POST':
        form = PurchaseForm()
        ...
    else:
        raise ValueError("Method not allowed here")
    ...


```

стало:

```python
HTTP_POST = "POST"
class PurchaseView(View):
    allowed_methods = [HTTP_POST]
    
    def post(self, request):
        ....

```

Частая ошибка любителей функциональных контроллеров в джанго проверять каждый раз метод через строку напрямую.
Уже давно предоставлен удобный функционал для проверки и можно использовать конкретные константы, чтобы не опечататься,
 когда очередной раз будешь проверять метод запроса.

# Итого

В основном от проверок "на местах", которые зачастую расположены по всему коду и повторяются, действительно
 помогает подняться на уровень абстракций повыше и не допускать ошибку в принципе. Такой подход логичен, но требует
 более вдумчивой работы с кодовой системой и не такой прямолинейной реализации. Поэтому зачастую такое чинится при рефакторинге
 или пересмотре проекта. Так намного легче начинать новые проекты, но действительно сложно перекраивать старые проекты под
 более архитектурно верный вид.