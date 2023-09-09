### Примеры кода и рефакторинг
Честно говоря, задание было понять трудновато, пришлось несколько раз вчитываться)

1. В системе была завязана работа на конкретных сущностях, которые предполагались быть жестко проименованы,
как только понадобилось расширить и унифицировать взаимодействее код стал в разы компактнее:
```python
for foo in bars:
        stats.type.A.foobar += ...
        stats.type.A.foobar += ...
        stats.type.B.foobar += ...
        stats.type.B.foobar += ...
        stats.type.C.foobar += ...
        stats.type.C.foobar += ...

```
```python
for board_info in boards_info.boards:
    for grade_name, grade_stat in board_info.grades.items():
        stats.grades[grade_name].millimeters += grade_stat.millimeters
        stats.grades[grade_name].pieces += grade_stat.pieces
```
Доступ к кокнретному типу исчез, зато ушла необходимость жесткого кодирования типов прямо в коде и гибкая обработка всех типов

2. Кейс с доступом к первому элементу попадающему под условие из генератора:
```python
need_element = None
for element in collection:
    if element == some_condition:
        need_element = element

if need_element is not None:
    ...
```
Здесь прекрасно все упаковывается в filter или generator comprehession, которые распаковываются функцией next() с возможностью
выбора дефолтного значения

```python
need_element = next(
    filter(lambda element: condition(element), collection),
    MY_DEFAULT_VALUE
)
# или без фильтра
need_element = next(
    (element for element in collection if condition(element)),
    MY_DEFAULT_VALUE
)
```

Во-первых, здесь мы явно пишем более идиоматический код, во-вторых способны использовать ленивые вычисления генераторов,
в-третьих задаем свое удобное дефолтное значение, если например, работаем с NullObject'ми

3. Использование нативных методов сортировки датаклассов
Зачастую, когда хотим сортировать датакласс, то приходится в каждом месте писать чт-то вроде:

```python
import dataclasses


@dataclasses.dataclass
class Item:
    name: str
    value:str
    index: str

def foo():
    items: List[Item] = [Item() for _ in range(100)]
    sorted_items = sorted(items, key=lambda item: item.index)
    return sorted_items
    
```
По итогу эти сортировки копятся и захламляют кодовую базу, сам инструмент предлагет лаконичное решение:

```python

@dataclasses.dataclass(order=True)
class Item:
    name: str = field(compare=False)
    value:str = field(compare=False)
    index: str = field(init=False, repr=False)


def foo():
    items: List[Item] = [Item() for _ in range(100)]
    return sorted(items)
```

### Итог

Зачастую многие абстрагирующие конструкции в языках требуют внимательного изучения документации и best-practices, потому что
такие ошибки обычно допускают начинающие программисты, привыкшие к решениям в лоб.
Но находить способ как сделать свой код компактнее в несколько раз,
применив нужную абстракцию всегда огромное удовольствие. Также помогает насмотренность из других языков, чтобы подмечать
схожие кейсы и использовать уже известную и эффективную абстракцию.