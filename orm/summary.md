1. ORM 
Самые популярные ORM для Python - sqlalchemy и DjangoORM. Так как я не пользовался первой, буду описывать только
Django. 
Основные сущности для работы с БД в ней это: 
- модели(models), сущности, которые описывают саму таблицу БД и ее поля.
- Результаты запросов, которые мы получаем и преобразуем в другие запросы QuerySet, по умолчанию ленивы, 
но имеют много неочевидных способов исполниться в рантайме раньше времени и занять много времени.
- менеджеры(managers), обертки для QuerySet, по мнению авторов фреймворка и многих писателей книг на тему организации
проекта с Django, нужны для изначального разделения работы с разными типами одной модели(менеджер для обычных пользователей
и для модераторов, менеджер для товаров в наличии и отсутствующих)

Сами запросы к БД описаны простым языком:
```python
class User(Model):
    username = CharField()
    type = CharField(choices=USER_TYPES)

users = User.objects.all() # все 
user = User.objects.get(id=given_id) # конкретный по id
moderators = User.objects.filter(type=USER_TYPES.MODERATOR) # фильтрация
User.objects.delete(id=given_id) # удаление по id
User.objects.update(id__in=list_id) # обновление по фильтрации списком
User.objects.count() # агрегация
```
Сами запросы достаточно очевидны и понятны, переводятся в SQL нормально, до момента работы с связанными таблицами
или сложной агрегации.

Способы выстрелить себе в ногу:
- привести QuerySet к списку = исполнение раньше времени
- Узнать длину QuerySet = исполнение раньше времени
- Взять слайс = моментальное исполнение
- Итерация по QuerySet = моментальное исполнение

Есть инструмент - **[Debug toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/)** , без которого 
оптимизация работы запросов невозможна. Он показывает время, сам запрос и кол-во запросов.

По моему мнению чистый SQL подходит для работы с такими вещами как ClickHouse, где работы ОРМ абсурдна и невозможна.
В самом фреймворке можно обойтись нужным набором правил, чтобы не плодить 1000к запросов в секунду.


2. Примеры как не надо и как надо
    - Проблема n+1 и запросы к таблицам со связью "1 к n" и "n то n":
   
   ```python
    class Car(Model):
        owner = ForeignKeyField(model=Human,related_name="cars",)
       
   class Human(Model):
        name = CharField()
   ```
   Плохо:
   ```python
   # people with theirs cars
   people = Human.objects.all()
   for human in people:
        print(human.cars)
   # тут для каждого человека доп. запрос на его тачки
   
    ```
    Получше:
    ```python
   # people with theirs cars
   people = Human.objects.all().select_related("cars")
   for human in people:
        print(human.cars)
   # SELECT * FROM Human INNER JOIN Car on (Human.id = Car.owner) изначально и никаких доп.запросов
    ```
    Много-ко-многим
    ```python
        class Car(Model):
            owners = ManyToManyField(model=Human, related_name="cars",)
            
                
       class Human(Model):
            name = CharField()
       ```
   Как надо:
   ```python
    Human.objects.all().prefetch_related("cars") 
   # два запроса:
   # Select * from Human
   # select * from Car where id in (%s,...)  с айдишниками из первого запроса
    ```
   - Оптимизация фильтрации при связи M2M
   Как не надо:
   ```python
   class Shop(Model):
        products_in_shop = ManyToManyField(model=ProductType, related_name="shops",)
        is_active = BooleanField()
            
                
    class ProductType(Model):
        name = CharField()
    
    # all active shops for every product type
   active_product_types = ProductType.objects.prefetch_related("shops").all()
   for product_type in active_product_types:
        print(product_type.shops.filter(is_active=True))
   
   
    ```
   Тут произойдет что: запрос для все типов продуктов, потом префетч запрос для всех магазинов, а потом 1 запросу
на каждый магазин для фильтрации)
Поэтому настраиваем prefetch
    ```python
    active_product_types = ProductType.objects.prefetch_related(
         Prefetch(
         "shops",
         queryset=Shop.objects.filter(is_active=True),
         to_attr="active_shops"
        )
    )\
    .all()
    for product_type in active_product_types:
         print(product_type.active_shops)
     
    ```
   Теперь запроса будет статично 2 и не больше: для магазинов и типов товаров.
   - создание множества объектов
   на первом проекте, я еще не знал о bulk-методах и любил создавать каждый объект с отдельным запросом.
   Теперь я кое-что знаю и понимаю, что достаточно одного запроса:
   ```python
    # не надо
    for name in names:
        author = Author(name=name)
        author.create()
    
    # надо 
    authors = [Author(name=name) for name in names]
    Author.objects.bulk_create(authors)
    ```
    Казалось вещь очевидная и простая, но часто встречается в проектах и замедляет работу.

### Выводы

В первую очередь для оптимизации фреймворка необходимо использовать не только голый фреймворк, но распределять
нагрузку данными на разные сервисы: PostgreSQL, Redis, ClickHouse. 
Глобально, я занимался оптимизацией запросов для джанго и могу сказать, что 80% потребностей бизнеса зачастую
покрывает верное использование ОРМ без ошибок новичков. Для более крупных систем и БД, зачастую приходится 
использовать сам SQL по себе, и это имеет свои нюансы: мы платим читаемостью и удобством в угоду оптимизации,
хотя, если увидеть некоторые запросы django orm, это можно легко опровергнуть.
Главный аспект - ORM не должна лезть в предметный домен приложения и бизнес-логику слишком сильно,
 иначе получится итерация по БД внутри вычислений важного функционала и God Objects на каждом шагу.
ORM достаточно неплохи для небольших проектов и данных, но для крупных вещей стоит конечно исопльзовать чистый
SQL и собственные мапперы, если потребуются.