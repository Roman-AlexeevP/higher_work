## Уровень классов

1. В проекте на Django есть класс сервис `ScreenFullInfoService` на 800+ строк, который собирает всю информацию о 
конкретной сущности системы. При это делает он все: от сбора статистики, до запросов в бд и вычислений,
связанных с бизнес-логикой.
Почему так скорее всего вышло:

Архитектура Django подстегивает размазывать логику по моделям/формам/сериализаторам/менеджерам, но когда 
необходима крупная комплексная работа по сбору информации это превращается в очень запутанную кодовую базу.
Поэтому зачастую есть подход выделить слой сервисов, который сцепляет слой данных и контроллеров API.
Что является не самой плохой идеей, но зачастую такие сервисы перегружаются, так как не являются частью какой-то
иерархии, а просто дублируют модели, например `BookService, AuthorService`, очевидно, что работа с 
 методами моделей и менеджеров тоже необходима, иначе подобные сервисы разрастаются до огромных размеров и нарушают SRP.

2. Слишком маленький класс

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def get_name(self):
        return self.name

    def get_age(self):
        return self.age


class PersonPrinter:
    def __init__(self, person):
        self.person = person

    def print_details(self):
        print(f"Name: {self.person.get_name()}")
        print(f"Age: {self.person.get_age()}")

```

В данном случае `PersonPrinter` является излишним, так как я считаю, что подобный функционал во-первых, можно
 реализовать в методе `__str__()` класса `Person`, во-вторых представление класса является частью его ответственности.
Данный пример мог бы быть корректным, если бы имелись разные классы под необходимые виды вывода: консоль, файл, окно приложения.
Такая ошибка возникает в результате преждевременной оптимизации, когда нет еще необходимости расширять какой-либо функционал
, а разработчик создает отдельный крошечный класс.

3. Метод из одного класса более подходит другому классу

```python
class Sale:
    def calculate_total(self, products):
        total = 0
        for product in products:
            total += product.price
        return total

class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price

class ShoppingCart:
    def __init__(self):
        self.products = []

    def add_product(self, product):
        self.products.append(product)

    def remove_product(self, product):
        self.products.remove(product)

    def calculate_total(self):
        sale = Sale()
        total = sale.calculate_total(self.products)
        return total
```

В данном примере метод `calculate_total` класса `ShoppingCart` явно предназначен для класса `Sale`. И его вызов необходимо
совершать отдельно.
Такая проблема возникает когда внутри класса **А** создается инстанс другого класса **В** и он используется 
только внутри класса **А**. ПРичиной возможно является неудачно вынесенная логика из класса или неверно
построенные взаимоотношения между классами.

4. Для данного примера подходят классы сериализаторы в Django, при их инициализации можно создать словарь `context`,
который зачастую заполняется по ходу движения от контроллера до бизнес-логики и обратно. Так получается, потому что
проще передать god-object, в котором все есть, чем продумать конкретное flow аргументов для каждой конкретной функции.
Например, необходимо протащить до сервиса данные из запроса и поэтому можно положить `request` в `context`.

5. 
```python
class Song:
    def __init__(self, title, artist):
        self.title = title
        self.artist = artist
        self.player = Player()

    def play(self):
        self.player.play_song(self.title)

class Player:
    def play_song(self, title):
        # реализация воспроизведения песни
        pass

```
В приведенном отрывке реализация класса `Song` зависит от реализации класса `Player`, если плееров будет несколько на выбор,
или он банально поменяет название, то мы должны будем изменять класс `Song`. Тут необходимо получать плеер через аргумент,
конструктора использовав прием Dependency Inversion. 
Такое может происходить при малом опыте в разработке или же когда при приоектировании не закладывается возможность расширяться,
получается сильная связность классов, что плохо сказывается на проекте)
6. такой пример найти/придумать не смог.
7. 
```python
class Image:
    def __init__(self, width, height):
        self.width = width
        self.height = height


    def save(self, file_path):
        # Логика сохранения изображения в заданном формате


class JPEGImage(Image):
    def save(self, file_path):
        # Логика сохранения изображения в формате JPEG

class ImageReader:
    def read(self, image):
        pass

class JPEGReader(ImageReader):
    def read(self, image):
        pass
```
В данном примере для создания класса `JPEGIMage` создается класс `JPEGReader`. В каких-то ситуациях это может быть
как и нормальным явлением, если мы заранее выделили место в проекте под расширения модуля работы с картинками. 
Но если это происходит так как классы чтения картинок полностью зависят от реализации класса картинок и мы делаем это, чтобы 
починить багы, тогда уже это неверно. ЛОгично, что данная проблема проистекает из сильной связности классов/модулей, которые
полагаются на детали технической реализации друг друга.
8. 
```python
class Image:
    def __init__(self, width, height):
        self.width = width
        self.height = height


    def save(self, file_path):
        # Логика сохранения изображения в заданном формате


class JPEGImage(Image):
    def save(self, file_path):
        # Логика сохранения изображения в формате JPEG


class PNGImage(Image):
    def save(self, file_path):
        # Логика сохранения изображения в формате PNG


```

В данном случае просходит переопределение метода `save()`, так как кажется наиболее логичным способом отнаследоваться.
Данная проблема решается либо через паттерн Visitor, либо через миксины. Возникает зачастую, когда путается композиция 
и наследование, т.е. нарушена иерархия классов.

## Уровень приложения

1. Любой пример кода, который изначально рассчитан на работу с одной сущностью и вся последующая логика спроектирована под это.
Например, мы делаем обработку только PNG фотографий, но не работаем с другими форматами, или мы обслуживаем windows, но не macOS.
Это возникает из-за ошибочного мнения, что система не будет выходить за рамки изначального ТЗ, 
также из хардкодинга платформо/формато/подставьте вашу боль зависимого значения
в коде, без нужных конструкций управления классами. Очевидно, что не стоит рассчитывать, что ваше приложение будет
универсально и идеально расширяемым с самого начала, но большинство практик хорошего проектирования рассчитаны на то,
чтобы изменения происходили точечно.
2. Данная проблема возникает, когда необходимо реализовывать временное решение для конкретной ситуации. 
Например скрипт преобразования конкретных данных из экселя случайного заказчика в формат вашей БД.
В данном случае может начаться проектирование решения, иерархия классов, паттерны, хотя достаточно обычного разделения
функционала с помощью декомпозиции без учета последующего расширения/рефакторинга.


## Резюме

Почти все эти ошибки проистекают еще со стадии проектирования приложения и обсуждения ТЗ с заказчиком/коллегами.
Мало кто пытается классифицировать решаемую проблему, выделить абстракции, поэтому возникают такие ошибки в классах/модулях.
Также часть ошибок возникает из страха избежать участи из первого абзаца и тотального оверинжиниринга, с целью учесть возможности 
расширения абсолютно ВСЕГО в проекте. Очевидный совет - изучать спецификацию своего продукта до разработки и подробно описывать ее,
 не забывая дополнять по мере роста. Тогда поддерживать и преоктировать кодовую базу будет намного комфортнее.