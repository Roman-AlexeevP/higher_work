# Задача 2

На вход приходит имя файла, директория и содержимое в виде словаря и вид операции.

- Если все параметры пустые то вернуть список файлов из директории
- Дальше если тип операции:
  - Удалить - удаляет файл или возбуждает исключение при отсутствии
  - Создать - создает файл и возбуждает исключение при наличии такого же и отсутствии содержимого, если содержимое есть то обновляет файл


Пишем первый тест и минимальную сигнатуру:

```python
from pathlib import Path


class Action:
    CREATE = 1
    DELETE = 2


def manage_files(directory: Path, filename: str = None, action: Action = None, content: dict = None):
    pass

```
```python
from pathlib import Path

import pytest

from tdd_paradigm.files import manage_files


@pytest.fixture
def test_files(tmp_path):
    files = []
    for i in range(10):
        file_path = tmp_path / Path(f"test_{i}.json")
        file_path.touch(exist_ok=True)
        files.append(file_path)
    return tmp_path, files

def test_files_list(test_files):
    tmp_dir, files = test_files
    result = manage_files(directory=tmp_dir)

    assert result == [file.name for file in files]

```

Добавляем первую реализацию и поправляем тест

```python
    if filename is None and action is None:
        return [file.name for file in directory.iterdir()]

--------------
  assert sorted(result) == ([file.name for file in files])
```

пишем тест на создание/обновление

```python
def test_create_file(temp_files):
    tmp_dir, files = temp_files
    test_content = {"test": "test"}
    test_filename = "new_file.json"
    manage_files(directory=tmp_dir, action=Action.CREATE, content=test_content, filename=test_filename)
    assert test_filename in [file.name for file in tmp_dir.iterdir()]
    new_test_content = {"test": "new_test"}
    manage_files(directory=tmp_dir, action=Action.CREATE, content=new_test_content, filename=test_filename)
    new_file = tmp_dir / test_filename
    with open(new_file, "r") as f:
        content = json.loads(f)
        assert content == new_test_content
```

Добавляем реализацию

```python
def create_file(filename: Path, content: dict):
    if filename.exists() and content is None:
        raise ValueError()
    with open(filename, "w") as f:
        json.dump(content, f)
    return filename


```


Пишем тест на удаление

```python

def test_delete_file(temp_files):
    tmp_dir, files = temp_files
    file_to_delete = files[0]
    manage_files(directory=tmp_dir, action=Action.DELETE, filename=file_to_delete)

    assert file_to_delete not in [file.name for file in tmp_dir.iterdir()]
    with pytest.raises(ValueError):
        manage_files(directory=tmp_dir, action=Action.DELETE, filename="non_existsing.png")
```

Пишем реализацию

```python

def delete_file(filename: Path, content: dict):
    if not filename.exists():
        raise ValueError()
    filename.unlink()
```


### Итого

Сделано 3 итерации:
- Список файлов
- СОздание/обновление
- Удаление


Потребовался 1 час времени.

В данном примере хотелось посмотреть как проходит процесс с простыми задачками, и выяснилось, что минимизировать шаги трудно.

Если есть декомпозиция по тестам, то все равно она выходит достаточно крупной, по комплексному тесту на задачу и постепенное написание кода
 до его успешного запуска.