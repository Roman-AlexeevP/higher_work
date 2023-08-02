# 1 

```python
class UserHandler:
    def __init__(self, database_connection):
        self.database_connection = database_connection

    def process_user(self, username, password, recipient, subject, message):
        self.authenticate_user(username, password)
        self.send_email(recipient, subject, message)


def handle_user(user_data):
    db_connection = DatabaseConnection()
    handler = UserHandler(db_connection)
    handler.process_user(
            user_data.username,
            user_data.password,
            user_data.recipient,
            user_data.subject,
            user_data.message
    )
```

В данном примере в строчку `handler.process_user` происходит фактическое нарушение SRP за счет совершения 
отправки письма и аутентификации юзера. Решением является постепенное разделение на два сервиса `EmailSender`
 и `AuthenticationService`, которые в свою очередь уже можно отдельно развивать и менять. Заодно стоит разделить принимаемые
 данные на данные о пользователе и данные для письма.

```python

class EmailSender:
    
    def __init__(self, email_backend):
        self.email_backend = email_backend
        
    def send_email(self, recipient, subject, message):
        # email logic
        pass
    
    
class AuthenticationService:
    
    def __init__(self, auth_backend, db_connection):
        self.auth_backend = auth_backend
        self.db_connection = db_connection
        
    def authenticate_user(self, username, password):
        # auth logic
        pass
    
def handle_user(user_data, email_data):
    db_connection = DatabaseConnection()
    auth_backend = BaseAuthenticationBackend()
    auth_service = AuthenticationService(auth_backend=auth_backend, db_connection=db_connection)
    auth_service.authenticate_user(user_data.username, user_data.password)
    email_sender = EmailSender()
    email_sender.send_email(email_data.recipient, email_data.subject, email_data.message)
    
```

# 2 

Пример класса, который получает данные от стороннего сервиса 1с в виде файла(пути), например, или что-то в этом роде, и записывает
 в комфортный для текущей компании формат базы данных.

```python
class DataProcessor:
    def __init__(self, file_path, database_connection):
        self.file_path = file_path
        self.database_connection = database_connection

    def parse_file(self):
        # Code to parse the data from a file and store it in a data structure

    def update_database(self):
        # Code to connect to the database and update it with the parsed data

    def process_data(self):
        self.parse_file()
        self.update_database()

# Usage
file_path = "data.txt"
db_connection = DatabaseConnection()
processor = DataProcessor(file_path, db_connection)
processor.process_data()

```

В данном примере проблемная строчка: `processor.process_data()`. Чтобы как-то навести порядок лучше все привести
к кокнретным возращаемым значениям и чистому потоку данных, для этого как минимум нужно 3 слоя:
1. чтение файла(`FileDataReader`),
2. Обработка данных (`DataProcessor`)(тут лучше называть по названиям из конкретной предметной области)
3. Чистая запись в БД (`DbWriter`), и то лучше реализовывать под каждую базу даннных свой кокнретный класс
и для организации работы общий класс или функция: `DataImporter`
```python

class FileReader:
 
    def __init__(self, file_path):
        self.file_path = file_path
    
    def parse_file(self):
        with open(self.file_path, "r") as file:
            data = file.read()
        return data

class DataProcessor:
 
    def __init__(self, raw_data):
        self.raw_data = raw_data
        
    def get_clean_data(self):
        clean_data = self.validate(self.raw_data)
        return clean_data

class DbWriter:
    
    def __init__(self, db_connection):
        self.db_connection = db_connection
        
    def write_data(self, data):
        # some db operations to write cleaned data
        pass

class DataImporter:
 
    def run(self):
        file_path = "data.txt"
        file_reader = FileReader(file_path)
        raw_data = file_reader.parse_file()
        data_processor = DataProcessor(raw_data)
        cleaned_data = data_processor.get_clean_data()
        db_connection = DatabaseConnection()
        writer = DbWriter(db_connection)
        writer.write_data(cleaned_data)

```

# 3

Получение типа и валидация в одном месте, собственный пример, с не самым удачными подходом.

```python

    def get_file_type(self):
        with zipfile.ZipFile(self.zip_file, "r") as archive:
            if archive.testzip() is not None:
                raise ValidationError()
            dirnames = archive.namelist()
            if any([dirname in DIRNAMES_1 for dirname in dirnames]):
                return SOME_TYPE_1
            elif any([dirname in DIRNAMES_2 for dirname in dirnames]):
                return SOME_TYPE_2
            raise ValidationError()


```

Здесь самым логичным способом было бы разделить валидацию и получение данных из архива в разные функции.

```python

def validate_archive(self):
    with zipfile.ZipFile(self.zip_file, "r") as archive:
        if archive.testzip() is not None:
            raise ValidationError()
        dirnames = archive.namelist()
    set_dirnames = set(dirnames)
    if not set_dirnames.intersection(set(DIRNAMES_1)) and not set_dirnames.intersection(set(DIRNAMES_2)):
        raise ValidationError()

def get_archive_type(archive_content):
    dirnames = set(archive_content.namelist())
    if dirnames.intersection(set(DIRNAMES_1)):
        return SOME_TYPE_1
    elif dirnames.intersection(set(DIRNAMES_2)):
        return SOME_TYPE_2
    return UNDEFIEND_TYPE
```


# 4 


Пример обработки сообщения в телеграм-боте, который отправялет скриншот по url

```python
async def on_message(message: types.Message, manager: UserHistoryManager):
    logger.info(f"URL: {message.text} from user: {message.from_user.id}")

    is_url_correct = await urls.check_url_status(message.text)
    if not is_url_correct:
        logger.warning(f"Wrong URL:{message.text} from user: {message.from_user.id}")
        await manager.log_action(user_id=message.from_user.id,
                                 url=message.text,
                                 success=False)
        return await message.reply(text_factory.get_wrong_url_text(), disable_web_page_preview=True)

    temp_photo = types.InputFile(path_or_bytesio=f"{consts.MEDIA_DIR_NAME}loading.png")
    temporary_message = await message.answer_photo(photo=temp_photo, caption="Запрос отправлен на сайт")

    page_detail = await screenshots.save_screenchot(message=message)

    photo = types.InputMediaPhoto(media=types.InputFile(page_detail.screenshot_path),
                                  caption=text_factory.get_screenshot_caption(page_detail))

    keyboard = whois_keybord_factory(page_detail.url)
    await manager.log_action(user_id=message.from_user.id,
                             url=page_detail.url,
                             success=True)
    await temporary_message.edit_media(media=photo, reply_markup=keyboard)

```

Здесь в функцию АПИ телеграмма затесалась логика обработки и логгирования событий, поэтому разделим обработку
 и функции АПИ в разные функции

```python

    
async def send_url_error_message(message):
     logger.warning(f"Wrong URL:{message.text} from user: {message.from_user.id}")
     await manager.log_action(user_id=message.from_user.id,
                                 url=message.text,
                                 success=False)
    return await message.reply(text_factory.get_wrong_url_text(), disable_web_page_preview=True)
async def send_temporary_photo():
    temp_photo = types.InputFile(path_or_bytesio=f"{consts.MEDIA_DIR_NAME}loading.png")
    temporary_message = await message.answer_photo(photo=temp_photo, caption="Запрос отправлен на сайт")
    await temporary_message

async def update_temporary_photo(original_message, temporary_message):
 
    page_detail = await screenshots.save_screenchot(message=original_message)

    photo = types.InputMediaPhoto(media=types.InputFile(page_detail.screenshot_path),
                                  caption=text_factory.get_screenshot_caption(page_detail))

    keyboard = whois_keybord_factory(page_detail.url)
    await manager.log_action(user_id=original_message.from_user.id,
                             url=page_detail.url,
                             success=True)
    await temporary_message.edit_media(media=photo, reply_markup=keyboard)

async def on_message(message: types.Message, manager: UserHistoryManager):
    logger.info(f"URL: {message.text} from user: {message.from_user.id}")

    is_url_correct = await urls.check_url_status(message.text)
    if not is_url_correct:
        await send_url_error_message(message)
        
    temp_photo = await send_temporary_photo()
    await update_temporary_photo(message, temp_photo)
    
```

Теперь разделены кейсы обработки фотографии и ошибки, сопровождать такой код проще.


# 5 

Функция получения файлов из заданного пути и проверка существования папки в одном месте.

```python
    def get_board_defects(self, collection_name, cut_id, board_id):
        collection_dir = Path(self.collections_dir / collection_name / cut_id)
        if not collection_dir.exists():
            raise CollectionManagerError()

        json_files = [
            file
            for file in collection_dir.iterdir()
            if file.name.startswith(board_id) and file.name.endswith(".json")
        ]
        return json_files
```

Опять перемешана логика валидации и кокнретное получения списка файлов, разделяем валидацию, логику и получение
 конкретного пути на три функции

```python
def check_folder_exists(folder_path):
    if not folder_path.exists():
        raise CollectionManagerError()
def get_board_defects(collection_dir, board_id):
        json_files = [
            file
            for file in collection_dir.iterdir()
            if file.name.startswith(board_id) and file.name.endswith(".json")
        ]
        return json_files

def get_collection_dir(self, collection_name, cut_id, board_id)
    return Path(self.collections_dir / collection_name / cut_id)

```


# Итого

Зачастую причиной нарушение SRP является либо излишняя спешка, что очевидно, либо в том числе вопрос производительности.
В моих примерах разве что работа с архивом может иметь незначительные просадки при работе с нескольким открываниями файла, но 
в основном я нарушал данный принцип больше из-за лени, так как банально удобнее и проще сказать "все в одном месте, думать меньше, писать меньше - круто".
Но в большинстве случаев я разделяю функционал по функциям, потому что код становится совершненно очевидным и простым для чтения.
Когда ты видишь для каждого действия свой инструмент, а не огромный `process_data` и `make_cool` работать становится приятно.ц

Так же важно не перебарщивать с интерпретацией этого принципа и не разделять каждый микрошаг на функцию, иначе кодовая база
 превратится в лапшу.
