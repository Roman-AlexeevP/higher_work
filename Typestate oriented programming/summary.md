### 1 кейс

Имеется сущность, которая заполняется постепенно в стороннем сервисе/процессе и выдает различный результат
в зависимости от состояния: начата, непроинициализирована, в процессе, готова.
```python
import dataclasses

@dataclasses.dataclass
class LongCalculatedEntity:
    name: str
    # ... another fields

    
```

Заменим явным состоянием из enum и воспользуемся питоновским паттерн-матчингом по делу:

```python
import dataclasses
from enum import Enum


class EntityState(Enum):
    EMPTY = 0
    STARTED = 1
    PROCESSED = 2
    FINISHED = 3

@dataclasses.dataclass
class Entity:
    general_fields: dict
    state: EntityState = EntityState.EMPTY


@dataclasses.dataclass
class StartedEntity(Entity):
    # ...
    started_fields: dict
    state: EntityState = EntityState.STARTED
    pass

@dataclasses.dataclass
class ProcessingEntity(Entity):
    processed_fields: dict
    # ...
    state: EntityState = EntityState.PROCESSED
    pass

@dataclasses.dataclass
class FinishedEntity(Entity):
    finished_fields: dict
    # ...
    state: EntityState = EntityState.FINISHED
    pass

def process_entity(entity: Entity):
    match entity.state:
        case EntityState.EMPTY:
            pass
        case EntityState.STARTED:
            pass
        case EntityState.PROCESSED:
            pass
        case EntityState.FINISHED:
            pass


```

Пример простой, но позволяет обрабатывать явно состояния. Если бы можно до рантайма узнать непокрытые случаи,
то вообще была сказка.


# кейс 2

Обработка удаленных сущностей и фильтрация.

```python
import dataclasses


@dataclasses.dataclass
class Video:
    is_deleted: bool
    

    def get_info_from_timecode(self):
        if is_deleted:
            ...
        ...
```

Намного лучше выделить отдельный класс с корректной ошибкой, чтобы можно было выявить проблемы при отладке:

```python
import dataclasses


@dataclasses.dataclass
class Video:
    
    def get_info_from_timecode(self):
        pass
    
@dataclasses.dataclass
class DeletedVideo:
    
    def get_info_from_timecode(self):
        raise TypeError("deleted videos dont support this operations")

```

# кейс 3

Не из питона, но показывает как реализуется версионирование структуры с обработкой каждой версии без Option типов.

```
#[superstruct(variants(V1, V2))]
pub struct Request {
    pub start: u16,
    #[superstruct(only(V2))]
    pub end: u16,
}

impl Request {
    pub fn process_request(&self){
        match self {
            RequestV1(request) => (),
            RequestV2(request) => (),
        }
    }
}

```

Это не прямое использование состояний, но возможность зафиксировать версию как отдельное состояние через 
enum и покрывать каждую выделенную версию кодом, так, чтобы компилятор не допускал нереализованных методов 
для всех случаев.


### Выводы

Подход работы с состояниями через отдельный класс/enum особенно продуктивен, если компилятор умеет адекватно
работать с sum types и отображать непокрытые случаи. В языках с динамической типизацией не так просто подчинить
себе покрываемость кода даже с анализатором как mypy. Но это все равно уменьшает когнитивную нагрузку, когда
структура описывает свои состояния явно и сервис по обработки так же явно каждое из состояний обрабатывает.
В идеале стоило бы стремится к покрытию большинства ошибок компилятором с помощью системы типов, так как машина
в любом случае будет умнее. Но для стоит использовать подходящие языки и хорошо проработанную предметную область.
