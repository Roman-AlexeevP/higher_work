### Листинг кода:
```python
class Application(Any):

    def __init__(self, config: AppConfiguration):
        self.config = config
        self.user: Optional[User] = None

    def run(self):
        self.launch_db()
        self.init_user()

    def launch_db(self):
        db_init_manager = InitManager(db_config)
        db_init_manager.init_database()

    def init_user(self):
        self.user = User()
        game_hero_manager = GameHeroManager()
        tasks_manager = TaskManager()
        self.user.set_game_hero_manager(game_hero_manager)
        self.user.set_task_manager(tasks_manager)
        self.user.init_game_hero()
        self.user.init_tasks()


```
### Комментарий на уровне системы

Этот класс является входной точкой в программу. Его назначение:
- Проинициализировать основные модули в системе
- Выдать в рантайме каждому модуле свою часть настроек/конфига
Тем самым он связывает модуль GUI и модуль с основной логикой, грубо говоря фронтенд с бекендом.