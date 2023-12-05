### Смысл данных в проектах

#### 1 кейс: редактирование данных, вместо явной передачи в функцию

В некоторых случаях происходят правки кода, добавление новой функциональности и 
вместо прямой передачи данных для вычисления новых полей неизменяемой по сути структуры начинается
редактирование "на местах":

Было:
```python
annotations = get_annotations(foo, bar)
annotations["images"][0]["height"] = mask.shape[0]
annotations["images"][0]["width"] =  mask.shape[1]
```

Достаточно добавить данные в функцию "конструктор", а еще лучше использовать dataclass(frozen=True)

Стало:
```python
annotations: Annotation = get_annotations(foo, bar, mask)
```

Тем самым пропадает обращение по индексам, лишняя модификация и появляется возможность сделать 
аннотации иммутабельными.

#### 2 кейс: использовать нужные структуры данных вместо мутабельности

Нам необходимо получить структуру данных, преобразовав другую структуру, причем первый и последний элемент
должны иметь особенную обработку в зависимости от второго и предпоследнего элемента соответственно.

Поэтому здесь приходит на помощь обыкновенный двусвязный список, который позволяет нам выделить обработку 
head, tail а также проверить следующий после головы и предшествующий хвосту элементы, либо в случае массиве,
 а именно списка в python мы можем переместить проверку в цикл

Было:
```python
new_items = []
for item in items:
    new_item = processe_item(item)
    new_items.append(new_item)
if len(new_items) > 1:
    new_items[1] = ...
    new_items[-1] = ...

```

Стало:

```python
def proccess_first_element(first, second):
    pass

def process_last_element(last, pre_last):
    pass

new_items = []
for i, item in enumerate(items):
    if i == 0:
        new_items.append(proccess_first_element(item, items[i+1]))
        continue
    if i == len(items) - 1:
        new_items.append(process_last_element(item), items[i-1])
        continue
    new_item = processe_item(item)
    new_items.append(new_item)
```

#### 3 кейс модели работы с API

Для каждой модели API важно, чтобы она соответствовала схеме и значения были равным тем, что пришли из бизнес-слоя
, поэтому для всех моделей Pydantic выставляем frozen=True

```python
class MyPydanticModel(BaseModel, frozen=True):
    title: str
    value: int | float  
```


### Выводы 

В большинстве случаев мутабельность данных используется как некий хак, либо как более простой способ модификации 
логики, исправление бага и т.д. 
Но при этом, мы расплачиваемся большей хаотичностью системы и множественными неявными состояниями и значениями.
Я не уверен, что всегда железно надо стоять на иммутабельности, но от 80% до 95% ваших данных должны быть иммутабельными,
 чтобы разрабатывать продукт было проще и он становился надежнее. На данный момент, я сам иногда применяю 
такие хитрости и костыли, чтобы что-то поправить или добавить, но если изначально задумавыть устойчивую структуру,
 то расширение происходит более комфортно, поэтому важно уделять время проектированию данных в вашей программе.
