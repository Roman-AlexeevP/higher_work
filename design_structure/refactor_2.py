import dataclasses
from pathlib import Path
from typing import List


@dataclasses.dataclass
class DbConfig:
    db_name: str
    path_to_init_scripts: str
    scripts_to_run: List[str]
@dataclasses.dataclass
class AppConfiguration:
    db_config: DbConfig

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


class InitManager(DbDriver):
    OPEN_SCRIPT_OK = 1
    OPEN_SCRIPT_ERROR = 2
    OPEN_SCRIPT_INIT = 3

    def __init__(self, db_config: DbConfig):
        super().__init__(db_config.db_name)
        self.config = db_config
        self.open_script_status = self.OPEN_SCRIPT_INIT

    def get_script_from_file(self, filename: Path) -> str:
        if not filename.exists():
            logger.error(f"{filename.name} not exists!")
            self.open_script_status = self.OPEN_SCRIPT_ERROR
            return
        with filename.open(mode="r") as sql_script:
            query = sql_script.read()
        self.open_script_status = self.OPEN_SCRIPT_OK
        return query

    def check_db_exists(self):
        is_file_exists = Path(self.config.db_name).exists()
        return is_file_exists


    def init_database(self):
        if self.check_db_exists():
            logger.info("Db is ready. Scripts part skiped")
            return
        logger.info("Starting DB initialization")
        failed_scripts = []
        init_scripts_path = Path(db_config.path_to_init_scripts)
        for script in self.config.scripts_to_run:
            script_path = init_scripts_path / script
            query = self.get_script_from_file(script_path)
            if self.open_script_status == self.OPEN_SCRIPT_ERROR:
                failed_scripts.append(script_path.name)
                continue
            self.query(query)
            logger.info(f"{script_path.name} successfully initiate")
        if failed_scripts:
            self.describe_failed_files(failed_scripts)

    def describe_failed_files(self, failed_filenames: List[str]):
        logger.error(
            f"Failed files count: {failed_filenames.count()}\n" + \
            "\n".join(failed_filenames)
        )
