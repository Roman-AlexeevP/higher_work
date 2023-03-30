# Цикломатическая сложность
1)
Код рефакторинга
```py
def writer(user_id: int, serializer_data: dict) -> None:  
    """Модуль записи свежей информации в кеш для пользователя"""  
    old_data = cache.get(user_id)  
    if old_data:  
        name_lnk = serializer_data.get("linkName", False)  
        if isinstance(name_lnk, str):  
            if len(name_lnk) == 0:  
                bad_word = [  
                    "https://www.",  
                    "http://www.",  
                    "https://",  
                    "http://",  
                    "wwww.",  
                ]  
                obj_long_lnk = serializer_data.get("longLink")  
                for objs in bad_word:  
                    len_objs = len(objs)  
                    if objs == obj_long_lnk[0:len_objs]:  
                        name_lnk = obj_long_lnk[len(objs) :]  
                        break  
        lnk_id = serializer_data.get("linkId")  
        stop_date = serializer_data.get("linkEndDate")  
        if isinstance(stop_date, type(None)):  
            serializer_data["linkEndDate"] = "-1"  
        re_clicked_today = cache.get(f"statx_aclick_{user_id}_{lnk_id}")  
        clicked_today = cache.get(f"statx_click_{user_id}_{lnk_id}")  
        if not isinstance(re_clicked_today, int):  
            re_clicked_today = 0  
        if not isinstance(clicked_today, int):  
            clicked_today = 0  
        fake_data = serializer_data  
        if name_lnk:  
            fake_data["linkName"] = name_lnk  
        start = fake_data.get("linkStartDate")  
        create = fake_data.get("linkCreatedDate")  
        formated_time = create.strftime("%Y-%m-%dT%H:%M")  
        if isinstance(start, type(None)):  
            fake_data["linkStartDate"] = formated_time  
        fake_data["linkCreatedDate"] = formated_time  
        if len(fake_data.get("linkPassword")) > 0:  
            fake_data["lock"] = True  
        else:  
            fake_data["lock"] = False  
        fake_data["statistics"] = {  
            "country": {},  
            "device": {  
                "1": 0,  
                "2": 0,  
                "3": 0,  
            },  
            "hours": {  
                0: 0,  
                1: 0,  
                2: 0,  
                3: 0,  
                4: 0,  
                5: 0,  
                6: 0,  
                7: 0,  
                8: 0,  
                9: 0,  
                10: 0,  
                11: 0,  
                12: 0,  
                13: 0,  
                14: 0,  
                15: 0,  
                16: 0,  
                17: 0,  
                18: 0,  
                19: 0,  
                20: 0,  
                21: 0,  
                22: 0,  
                23: 0,  
                24: 0,  
            },  
            "reClickedToday": re_clicked_today,  
            "clickedToday": clicked_today,  
        }  
        old_data.insert(0, OrderedDict(fake_data))  
        # old_data.append(OrderedDict(fake_data))  
        timer = int(cache.ttl(user_id))  
        cache.set(user_id, old_data, timer)
```

1) Убираем сразу условие на ранний выход
2) Выносим обработку данных из кэша в отдельную функцию, а вставку оставляем тривиальной
```py
@staticmethod  
def writer(user_id: int, serializer_data: dict) -> None:  
    """Модуль записи свежей информации в кеш для пользователя"""  
    old_data = cache.get(user_id)  
    if not old_data:  
        return  
    new_data = proccess_user_data(user_id, serializer_data)  
    old_data.insert(0, OrderedDict(new_data))  
    timer = int(cache.ttl(user_id))  
    cache.set(user_id, old_data, timer)
```
1) Меняем выдачу булева значения в однострочный вид:
```py
if len(fake_data.get("linkPassword")) > 0:  
    fake_data["lock"] = True  
else:  
    fake_data["lock"] = False
--->
fake_data["lock"] = len(fake_data.get("linkPassword")) > 0
```
2) Приводим работу с именем ссылки и самой ссылкой в отдельную функцию и активно используем дефолтные значения словаря для избежания None случаев
```py
UNCORRECT_VARIANTS = [  
        "https://www.",  
        "http://www.",  
        "https://",  
        "http://",  
        "wwww.",]

fake_data["linkName"] = process_name_link(  
    name_link=serializer_data.get("linkName", ""),  
    full_link=serializer_data.get("longLink", "")  
)
def process_name_link(name_link: str, full_link: str) -> str:  
    if len(name_link) != 0:  
        return name_link  

    for bad_word in UNCORRECT_VARIANTS:  
        if full_link.startswith(bad_word):  
            valid_link = full_link.replace(bad_word, "")  
            return valid_link
```

3) Доводим до ума дефолтные значения
```py
re_clicked_today = cache.get(f"statx_aclick_{user_id}_{lnk_id}", 0)  
clicked_today = cache.get(f"statx_click_{user_id}_{lnk_id}", 0)  
created_date = serializer_data.get("linkCreatedDate").strftime("%Y-%m-%dT%H:%M")  
started_date = serializer_data.get("linkStartDate", created_date)  
fake_data["linkStartDate"] = started_date  
fake_data["linkCreatedDate"] = created_date
```
 Итог: с 12 до 4 и 1 сложности при записи кэша
линтинг:

```py
BAD_WORDS = [  
        "https://www.",  
        "http://www.",  
        "https://",  
        "http://",  
        "wwww.",  
    ]  
  
  
def process_name_link(name_link: str, full_link: str) -> str:  
    if len(name_link) != 0:  
        return name_link  
    for bad_word in BAD_WORDS:  
        if full_link.startswith(bad_word):  
            valid_link = full_link.replace(bad_word, "")  
            return valid_link  
  
def proccess_user_data(user_id: int, serializer_data: dict):  
    fake_data = dict(serializer_data)  
    fake_data["linkName"] = process_name_link(  
        name_link=serializer_data.get("linkName", ""),  
        full_link=serializer_data.get("longLink", "")  
    )  
    lnk_id = serializer_data.get("linkId")  
    fake_data["linkEndDate"] = serializer_data.get("linkEndDate", "-1")  
    re_clicked_today = cache.get(f"statx_aclick_{user_id}_{lnk_id}", 0)  
    clicked_today = cache.get(f"statx_click_{user_id}_{lnk_id}", 0)  
    created_date = serializer_data.get("linkCreatedDate").strftime("%Y-%m-%dT%H:%M")  
    started_date = serializer_data.get("linkStartDate", created_date)  
    fake_data["linkStartDate"] = started_date  
    fake_data["linkCreatedDate"] = created_date  
    fake_data["lock"] = len(serializer_data.get("linkPassword")) > 0  
    fake_data["statistics"] = {  
        "country": {},  
        "device": {  
            "1": 0,  
            "2": 0,  
            "3": 0,  
        },  
        "hours": {  
            0: 0,  
            1: 0,  
            2: 0,  
            3: 0,  
            4: 0,  
            5: 0,  
            6: 0,  
            7: 0,  
            8: 0,  
            9: 0,  
            10: 0,  
            11: 0,  
            12: 0,  
            13: 0,  
            14: 0,  
            15: 0,  
            16: 0,  
            17: 0,  
            18: 0,  
            19: 0,  
            20: 0,  
            21: 0,  
            22: 0,  
            23: 0,  
            24: 0,  
        },  
        "reClickedToday": re_clicked_today,  
        "clickedToday": clicked_today,  
    }  
    return fake_data

def writer(user_id: int, serializer_data: dict) -> None:  
    """Модуль записи свежей информации в кеш для пользователя"""  
    old_data = cache.get(user_id)  
    if not old_data:  
        return  
    new_data = proccess_user_data(user_id, serializer_data)  
    old_data.insert(0, OrderedDict(new_data))  
    timer = int(cache.ttl(user_id))  
    cache.set(user_id, old_data, timer)
```

2 пример:

Исходный вариант:
```py
def create_link(request_user: User) -> Union[bool, dict]:  
    if request_user.banned is False:  
        cnt_lnk = CacheModule.count_lnk(request_user.id)  
        if request_user.subs_type == "REG":  
            if int(cnt_lnk) < 75:  
                return True  
            cache.incr("server_user_reg_limit_lnk")  
            return {"error": "Лимит 75 ссылок, удалите не нужные"}  
        elif request_user.subs_type == "BTEST":  
            if cnt_lnk < 150:  
                return True  
            cache.incr("server_user_btest_limit_lnk")  
            return {  
                "error": "Для участников бета-тестирования" + "лимит 150 ссылок"  
            }  
        elif request_user.subs_type == "MOD":  
            return True  
        cache.incr("server_try_create_lnk_ban_usr")  
    else:  
        return {"error": "Учетная запись заблокирована"}

```

Редактированный вариант

```py
def create_link(request_user: User):  
    if request_user.banned:  
        return {"error": "Учетная запись заблокирована"}  
  
    count_link = CacheModule.count_lnk(request_user.id)  
  
    user_type_to_callback_mapping = {  
        "REG": RegisteredUserLimit,  
        "BTEST": BetaTesterLimit,  
        "MOD": ModeratorLimit,  
    }  
    user_limit = user_type_to_callback_mapping[request_user.subs_type](count_link)  
    cache.incr("server_try_create_lnk_ban_usr")  
    return user_limit.check_limit()  
  
  
class UserLimit:  
    LINK_LIMIT: int = 0  
    ERROR_MESSAGE: str = ""  
    CASHE_ACTION = ""  
  
    def __init__(self, count_link):  
        self.count_link = count_link  
        self.cache = cache  
  
    def check_limit(self) -> dict:  
        if self.count_link < self.LINK_LIMIT:  
            return True  
        cache.incr(self.CASHE_ACTION)  
        return self.ERROR_MESSAGE  
  
  
class RegisteredUserLimit(UserLimit):  
    CASHE_ACTION = "server_user_reg_limit_lnk"  
    ERROR_MESSAGE = {"error": "Лимит 75 ссылок, удалите не нужные"}  
    LINK_LIMIT = 75  
  
  
class BetaTesterLimit(UserLimit):  
    CASHE_ACTION = "server_user_btest_limit_lnk"  
    ERROR_MESSAGE = {  
        "error": "Для участников бета-тестирования" + "лимит 150 ссылок"  
    }  
    LINK_LIMIT = 150  
  
  
class ModeratorLimit(UserLimit):  
  
    def check_limit(self):  
        return True
```

Итог: с 7 до 1 цикломатической сложности благодаря маппингу и использованию параметрическому полиморфизму для разных типов лимитов по юзерам

3) Пример сложность 7 до 3
Исходный код:
```py
def post(self, request: HttpRequest) -> Response:  
    if cache.get("registrations_on_site"):  
        eml_obj = request.data.get("email", False)  
        if eml_obj:  
            if User.objects.filter(email=eml_obj).exists():  
                msg = "Email уже зарегестрирован"  
                return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)  
        if request.user.is_anonymous:  
            serializer = self.serializer_class(data=request.data)  
            if serializer.is_valid(raise_exception=True):  
                serializer.save()  
                user_instance = serializer.instance  
                refresh = MyTokenObtainPairSerializer.get_token(user_instance)  
                data = {  
                    "email": str(user_instance),  
                    "access": str(refresh.access_token),  
                }  
                data = Response(data, status=status.HTTP_200_OK)  
                data.set_cookie(  
                    key="refresh",  
                    value=str(refresh),  
                    expires=5184000,  
                    secure=True,  # рансервер не поддерживает https  
                    httponly=True,  
                )  
                data.set_cookie("registration_elink", max_age=2592000)  
                id_email_user = {  
                    "id": user_instance.id,  
                    "email": user_instance.email,  
                }  
                RegMail.send_code.delay(id_email_user)  
                cache.incr("server_new_users")  
                return data  
        if serializer.errors.get("email", False):  
            msg = {"error": "Пользователь с таким email уже существует"}  
        else:  
            ServerStat.reported(  
                "RegistrationAPIView_129",  
                f"Ошибка регистрации: {serializer.errors}",  
            )  
            msg = {"error": "Ошибка регистрации, обратитесь в поддержку"}  
            cache.incr("server_error_register")  
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)  
    msg = {"error": "Извините, регистрация временно приостановлена"}  
    return Response(msg, status=status.HTTP_400_BAD_REQUEST)
```

Конечный код:
```py
def process_anonymous_user(self, serializer):  
    serializer.is_valid(raise_exception=True)  
    serializer.save()  
    user_instance = serializer.instance  
    refresh = MyTokenObtainPairSerializer.get_token(user_instance)  
    data = {  
        "email": str(user_instance),  
        "access": str(refresh.access_token),  
    }  
    data = Response(data, status=status.HTTP_200_OK)  
    data.set_cookie(  
        key="refresh",  
        value=str(refresh),  
        expires=5184000,  
        secure=True,  # рансервер не поддерживает https  
        httponly=True,  
    )  
    data.set_cookie("registration_elink", max_age=2592000)  
    id_email_user = {  
        "id": user_instance.id,  
        "email": user_instance.email,  
    }  
    RegMail.send_code.delay(id_email_user)  
    cache.incr("server_new_users")  
    return data  
  
  
def post(self, request: HttpRequest) -> Response:  
    if not cache.get("registrations_on_site"):  
        msg = {"error": "Извините, регистрация временно приостановлена"}  
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)  
  
    serializer = self.serializer_class(data=request.data)  
    if request.user.is_anonymous:  
        return self.process_anonymous_user(serializer)  
    ServerStat.reported(  
            "RegistrationAPIView_129",  
            f"Ошибка регистрации: {serializer.errors}",  
        )  
    msg = {"error": "Ошибка регистрации, обратитесь в поддержку"}  
    cache.incr("server_error_register")  
    return Response(msg, status=status.HTTP_400_BAD_REQUEST)
```

Развернуты условия, выделены отдельный метод для обработки незарегистрированных пользователей и валидация выделена в отдельный модуль, чтобы обработчик был минимален.
