### 1. Призрачное состояние
1. 
```python
def generator(name: str, **options: Dict[str, Any]) -> None:
    """Define generator generator command-line interface.

    Args:
        name (str): Given generator name.
        options (typing.Dict[str, typing.Any]): Map of command option names to
            their parsed values.

    """
    require_fastapi_mvc_project()
    name = name.lower().replace("-", "_").replace(" ", "_")
    data = {
        "generator": name,
        "nix": not options["skip_nix"],
        "repo_url": options["repo_url"],
        "github_actions": not options["skip_actions"],
        "license": options["license"],
        "copyright_date": datetime.today().year,
    }

    copier.run_copy(
        src_path=COPIER_GENERATOR.template,
        vcs_ref=COPIER_GENERATOR.vcs_ref,
        dst_path=f"./lib/generators/{name}",
        data=data,
        answers_file=".generator.yml",
    )
```
В данной функции заполняется изменяемый словарь, что добавляет неявных состояний.
Так как структура известна изначально, то можно сократить возможные проблемы иммутабельным датаклассом:

```python
import datetime
import dataclasses


@dataclasses.dataclass(frozen=True)
class ProjectInfo:
    generator_name: str
    skip_nix: bool
    repo_url: str
    skip_github_actions: bool
    license: str
    copyright_date: datetime.datetime


def generator(name: str, **options: Dict[str, Any]) -> None:
    require_fastapi_mvc_project()
    name = name.lower().replace("-", "_").replace(" ", "_")
    data = ProjectInfo(
            generator=name,
            nix=not options["skip_nix"],
            repo_url=options["repo_url"],
            github_actions=not options["skip_actions"],
            license=options["license"],
            copyright_date=datetime.today().year,
    )

    copier.run_copy(
            src_path=COPIER_GENERATOR.template,
            vcs_ref=COPIER_GENERATOR.vcs_ref,
            dst_path=f"./lib/generators/{name}",
            data=data,
            answers_file=".generator.yml",
    )
```
Теперь если использовать эту структуру по всему проекту, то разработчикам станет намного проще понимать, что
происходит.

2.  
```python
if job.is_finished:
    result = job.return_value()
    for car in result["info"]["cars"]:
        car["thumbnail"] = self.get_thumbnail_link(
            request=request,
        )
```
```python
if job.is_finished:
    result = job.return_value()
    cars_with_thubmnail = get_cars_thumbnails(result["cars_info"]["cars"])

```
Заменяем неявное обновление поля в словаре - получением нового иммутабельного объекта через вызов конкретной функции

### 2. Неточность
1. Неполная реализация для спецификации
Есть функция, которая читает статистику из файла, но не обрабатывает случай с несуществующим файлом, хотя
должна принимать такой аргумент и возвращать пустую статистику:
```python
    def get_stats(self, stats_path: Path):
        with stats_path.open() as stats_file:
            raw_stats = json.load(stats_file)

```
```python
    def get_stats(self, tats_path: Path):
        stats = Stats()
        if not stats_path.exists():
            return stats
        with stats_path.open() as stats_file:
            raw_stats = json.load(stats_file)
```
Добавили инициализацию пустого объекта с дефолтными значениями и возращаем корретный с точки зрения фронтенда
объект
2. 
```python
class Car:
    has_child_place: bool

def proccess_cars(cars: List[Car]):
    cars = list(filter(lambda  car: car.has_child_place, cars))
    ...
```
В данном пример выбираются только машины с детским местом, хотя по аннотации мы расчитываем на обработку всех видов машин
Поэтому мы должны либо расширить функционал, либо передавать точно уже отфильтрованные машины
```python
class Car:
    has_child_place: bool

def get_car_with_child_place(cars: List[Car]) -> List[Car]:
    return list(filter(lambda  car: car.has_child_place, cars)
    
def def proccess_cars(cars: List[Car]):
   pass

def process_cars_with_child_place(cars: List[Car]):
    pass
```
3. 
При старте трудоемкой задачи в запросе передается параметр boards_folders или collections,
что по факту не соответствует спецификации модели и случаи должны быть обработаны отдельно, 
что не приходилось проверять на пустые поля и вводить путаницу для клиента
```python

class JobStart(BaseModel):
    collections: Optional[list]
    boards_folders: Optional[list]
    search_string: Optional[str]

def start_job(job_start: JobStart):
        if job_start.boards_folders:
        collection_name = manager.create_new_collection(
            job_start.boards_folders, job_start.search_string, True
        )
        elif job_start.collections:
            collection_name = manager.create_new_collection(job_start.colections)
```
```python
class JobStartCollections(BaseModel):
    collections: list
    search_string: Optional[str]
    
class JobStartBoardsFolders(BaseModel):
    boards_folders: list
    search_string: Optional[str]

def start_job_collections(job_start_collections: JobStartCollections):
    manager.create_new_collection(job_start_collections.collections)
    
def start_job_boards_folders(job_start_boards_folders: JobStartBoardsFolders):
    manager.create_new_collection(job_start_boards_folders.boards_folders)

```
### 3. Интерфейс проще реализации
1. Мы не можем кратко описывать интерфейсы, когда важно понимание возвращаемого результат:
```python
@property
def sides(self) -> List[SideData]:
    """Return all sides if they exists, in order of getting it from camera capture module"""
    return sorted(
        [side for side in (self.surfaces + self.edges) if side is not None],
        key=lambda side: SURFACE_VIS_ORDER[side.side_id],
        )
```
В данном случае нам важно получать определенный список сторон в строго огооворенном порядке и спецификация 
сама по себе не может быть короче реализации(например, просто обозначив сигнатуру "sides")
2. 
```python
def init_database(self):
    logger.info("Starting DB initialization")
    failed_scripts = []
    for file in self.init_scripts:
        query = self.get_script_from_file(file)
        if self.open_script_status == self.OPEN_SCRIPT_ERROR:
            failed_scripts.append(file.name)
            continue
        self.query(query)
        logger.info(f"{file.name} successfully initiate")
    if failed_scripts:
        self.describe_failed_files(failed_scripts)
        
def describe_failed_files(self, failed_filenames: List[str]):
    logger.error(
        f"Failed files count: {failed_filenames.count()}\n" + \
        "\n".join(failed_filenames)
    )
```
В данном случае при чтении скриптов человеку не может быть понятно, что за скрипты и для чего они,
было корректно создать типы данных описывающие множество валидных скриптов и их назначение:
```python

SHELL_DUMP_SCRIPT = Path || str
SQL_CREATION_SCRIPT = Path || str
INIT_SCRIPTS = SQL_CREATION_SCRIPT || SHELL_DUMP_SCRIPT

class InitMAnager:
    def __init__(self, init_scripts: INIT_SCRIPTS):
        self.init_scripts = init_scripts

```

### Резюме

Действительно много глупых ошибок обнаруживается при наличии призрачных состояний, особенно в языках с 
динамической типизацией. Поэтому надо стараться использовать иммутабельные переменные и конкретные типы данных.
Неточности в основном влияют на когнитивную нагрузку читающего код и постепенное "Замыливание" глаза для разработчика,
 плотно работающего с кодом.
Основные усилия же стоит направлять на подробное описание спецификаций, чтобы при реализации все вопросы 3 уровне
мышления о программе были решены и ясны.
В моем случае часто видны кода, который не всегда однозначен и его спецификация недостаточна прозрачна.