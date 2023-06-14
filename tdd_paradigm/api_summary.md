                                                 1. выбрать задачу
2. придумать спецификацию
3. написать сразу тест
4. постепенно реализовывать с тестом
5. замерить кол-во шагов
6. просмотреть сколько шагов сделано и можно было ли меньше
7. повторить еще раз

# Задача 1

Получить с открытого [API](https://wizard-world-api.herokuapp.com/swagger/index.html) по Гарри Поттеру список волшебников и вернуть JSON 
с 5-ью волшебниками, у которых больше всего зелий

Изначальный тест
```python
from tdd_paradigm.wizards_api import sort_wizards, NEEDED_WIZARDS_COUNT


@pytest.fixture
def wizard_api_response():
    return [
        {"elixirs": [i for i in range(i)], "id": "", "firstName": "", "LastName": ""} for i in range(10, 1, -1)
    ]
# first test case
def test_wizard_api(wizard_api_response):

    wizards_list = wizard_api_response
    sorted_wizards_list = sort_wizards(wizards_list)
    assert len(sorted_wizards_list) == NEEDED_WIZARDS_COUNT
    


---------------------

NEEDED_WIZARDS_COUNT = 5

def sort_wizards(wizards_json):
    return wizards_json[:NEEDED_WIZARDS_COUNT]
```

```python
# first test case
def test_wizard_api(wizard_api_response):

    wizards_list = wizard_api_response
    # Добавляем шаг преобразования в сущности из json
    wizard_entities = wizards_factory(wizards_list)
    sorted_wizards_list = sort_wizards(wizard_entities)
    assert len(sorted_wizards_list) == NEEDED_WIZARDS_COUNT


```

добавляем реализацию:

```python
@dataclasses.dataclass
class Elixir:

    id: str = ""
    name: str = ""
@dataclasses.dataclass
class Wizard:
    id: str = ""
    elixirs: List[Elixir] = list
    first_name: str = ""
    last_name: str = ""
    
def wizards_factory(wizards_json: List[dict]) -> List[Wizard]:
    return [
        Wizard(
            first_name=wizard.get("firstName"),
            last_name=wizard.get("lastName"),
            id=wizard.get("id"),
            elixirs=[
                Elixir(
                    id=elixir.get("id"),
                    name=elixir.get("name")
                ) for elixir in wizard.get("elixirs")
            ],
        ) for wizard in wizards_json
    ]

# фиксим фикстуру

@pytest.fixture
def wizard_api_response():
    return [
        {"elixirs":
             [{"id": "", "name": ""} for i in range(i)],
         "id": "",
         "firstName": "",
         "LastName": ""} for i in range(10, 1, -1)
    ]
```

Функция сортировки - след.шаг

```python
def sort_wizards(wizards: List[Wizard]) -> List[Wizard]:
    return sorted(wizards, key=lambda wizard: len(wizard.elixirs))[:NEEDED_WIZARDS_COUNT]

```

Убираем получение ответа в отдельную функцию и обновляем тест
```python
def test_wizard_api():
    url = "https://wizard-world-api.herokuapp.com/Wizards"
    # убираем фикстуру в функцию и реализуем получение ответа АПИ
    wizards_list = get_wizards(url)
    # Добавляем шаг преобразования в сущности из json
    wizard_entities = wizards_factory(wizards_list)
    assert all(filter(lambda x: type(x) == Wizard, wizard_entities))
    sorted_wizards_list = sort_wizards(wizard_entities)
    assert len(sorted_wizards_list) == NEEDED_WIZARDS_COUNT


```

Дописываем реализацию и тестируем финальный вариант:

### Тест

```python

from tdd_paradigm.wizards_api import sort_wizards, NEEDED_WIZARDS_COUNT, wizards_factory, Wizard, Elixir, get_wizards


def test_wizard_api():
    url = "https://wizard-world-api.herokuapp.com/Wizards"
    # убираем фикстуру в функцию и реализуем получение ответа АПИ
    wizards_list = get_wizards(url)
    # Добавляем шаг преобразования в сущности из json
    wizard_entities = wizards_factory(wizards_list)
    assert all(filter(lambda x: type(x) == Wizard, wizard_entities))
    sorted_wizards_list = sort_wizards(wizard_entities)
    assert len(sorted_wizards_list) == NEEDED_WIZARDS_COUNT
    assert all(
        filter(
            lambda wizard: len(wizard.elixirs) <= len(sorted_wizards_list[0].elixirs),
            sorted_wizards_list
        )
    )


```

### Реализация

```python
import dataclasses
from typing import List

import requests as requests

NEEDED_WIZARDS_COUNT = 5


@dataclasses.dataclass
class Elixir:
    id: str = ""
    name: str = ""


@dataclasses.dataclass
class Wizard:
    id: str = ""
    elixirs: List[Elixir] = list
    first_name: str = ""
    last_name: str = ""


def get_wizards(url):
    response = requests.get(url)
    return response.json()


def wizards_factory(wizards_json: List[dict]) -> List[Wizard]:
    return [
        Wizard(
            first_name=wizard.get("firstName"),
            last_name=wizard.get("lastName"),
            id=wizard.get("id"),
            elixirs=[
                Elixir(
                    id=elixir.get("id"),
                    name=elixir.get("name")
                ) for elixir in wizard.get("elixirs")
            ],
        ) for wizard in wizards_json
    ]


def sort_wizards(wizards: List[Wizard]) -> List[Wizard]:
    return sorted(wizards, key=lambda wizard: len(wizard.elixirs))[:NEEDED_WIZARDS_COUNT]

```


### Итого

Сделано 4 итерации:
- Основной концепт
- Преобразование данных во внутренние сущности
- Обработка данных
- Получение данных и финальная "уборка"

Потребовался 1 час времени.

Можно было бы сделать более детализованные теста на каждый конкретный шаг, с проверкой статуса запроса, его тела.
Проверка краевых случаев и валидация преобразований в фабрике, а также несколько случаев для финальной проверки сортировки.
В целом, можно было идти более маленькими шагами, тогда бы и спецификации и сами реализации были бы подробнее.