# Реализация в языке

В python миксины реализуются таким образом:

```python

# Определим миксин для отображения в консоли параметров класс
class PrintableParamsMixin:
    
    def attributes(self):
        # data attributes
        for name, value in self.__dict__.items():
            print(f"{name:25}{str(value):<20}")


# СОздадим иерархию классов брони, чтобы к конечному наследнику добавить миксин
class Armor:
    
    def __init__(self, armor_points, armor_type):
        self.armor_points = armor_points
        self.armor_type = armor_type

# Указываем миксин слева от основного класса
class SteelArmor(Armor, PrintableParamsMixin):
    
    def __init__(self, armor_points):
        super().__init__(armor_points, armor_type="STEEL")

    
rich_steel_armor = SteelArmor(armor_points=1000)
rich_steel_armor.attributes() # используем метод миксина

```

MRO в python основан на depth-first, left-to-right принципах, это важно учитывать при порядке перечисления миксинов в 
классе.
В основнов известны по применениям в Django как для расширения model-layer и view-layer, например, есть такие базовые 
миксины из коробки: LoginRequiredMixin, UserPassesTestMixin, что позволяет расширять поведение своего слоя контроллеров.

Как действительно удобный инструмент считаю можно использовать для сериализации данных, отображения в каком-либо виде, например:

```python

# расширим инспекцию кода для отладки:

class AttributesMixin:
    @property
    def attributes(self):
        # data attributes
        for name, value in self.__dict__.items():
            print(f"{name:25}{str(value):<20}")
        # methods
        for name, value in self.__class__.__dict__.items():
            if not name.startswith('__'):
                print(f"{name:25}{str(value):<20}")
                
# также создадим миксин для отображение исходного кода
import inspect
class SourceCodeMixin:
    @property
    def sourcecode(self):
        return inspect.getsource(self.__class__)

class SomeDomainClass(BaseDomain, AttributesMixin, SourceCodeMixin):
    
    pass



```

В целом концепция миксинов позволяет удобно расширять классы библиотек собственным функционалом в виде удобной иерархии,
так например расширяли классы для админ-панели в рабочем проекте. Это более удобная альтернатива классическому Visitor, 
особенно в python. Я бы применял это для отладки/валидации/статистики.