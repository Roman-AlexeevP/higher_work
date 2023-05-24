class InitManager(DbDriver):
    OPEN_SCRIPT_OK = 1
    OPEN_SCRIPT_ERROR = 2
    OPEN_SCRIPT_INIT = 3

    def __init__(self, init_files: List[Path], db_name):
        super().__init__(db_name)
        self.init_scripts = init_files
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


class Application(Any):
    DEFAULT_SQL_SCRIPTS_PATH = "src/db/sql_scripts"

    def __init__(self, path_to_sql_scripts: str = DEFAULT_SQL_SCRIPTS_PATH, db_name=consts.DB_NAME):
        self.path_to_sql_scripts = path_to_sql_scripts
        self.db_name = db_name
        self.user: Optional[User] = None

    def run(self):
        self.launch_db()
        self.init_user()

    def launch_db(self):
        sql_files = self.get_files_from_folder(self.path_to_sql_scripts)
        db_init_manager = InitManager(init_files=sql_files, db_name=self.db_name)
        db_init_manager.init_database()

    def init_user(self):
        self.user = User()
        game_hero_manager = GameHeroManager(db_name=self.db_name)
        tasks_manager = TaskManager(db_name=self.db_name)
        self.user.set_game_hero_manager(game_hero_manager)
        self.user.set_task_manager(tasks_manager)
        self.user.init_game_hero()
        self.user.init_tasks()

    def get_files_from_folder(self, folder_name: str) -> List[Path]:
        folder_path = Path(folder_name)
        files = [file for file in folder_path.iterdir()]
        return files

    def exists_database(self) -> bool:
        return Path(self.db_name).exists()