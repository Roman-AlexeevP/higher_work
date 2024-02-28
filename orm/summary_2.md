### Неверные ожидания/работа стороннего библиотеки/фреймворка

1. Кейс с FastAPI: в начале изучения не придал значение тому, какая функция для эндпоинта синхронная или
асинхронная. Но позже выяснил, что асинхронные кидаются в event-loop, а синхронные запускаются в отдельном
пуле потоков. В асинхронные были блокирующие операции и соот-но все было не очень правильно. 
Ошибка моя, недоглядел документацию и теорию по блокирующим операциям.
2. Во время работы с discordpy написал самописное решение для подкоманд, потратил очень времени. Спустя полгода
решил плотно изучить документацию нашел готовое решение и отрефакторил по-человечески.
Ошибка опять же моя, документация нанесла очередной удар по моим костылям.
3. Не мой пример, но с работы: функция, которая из строки делает цвет из хеша работала по-разному для 
python и javascript, обнаружили не сразу на каких-то специфичных оттенках. По итогу техдир переписал 
функцию хеширования для питоновской версии и стало все одинаково.
Ошибка фреймворка, в этот раз не документации.

### Продуманный результат как основа безошибочного поведения

1. Порядок выдачи важен как для пользователя, так и для фронтенд-слоя: типовой пример
сортировка задач в банальном TODO. Для пользователя важно отображать задачи по приоритету и дате окончания, а
не по дате создания, например.
Для этого в dataclass можно задать полю свойство `order=True`, тогда список датаклассов по нему отсортируется.
2. Очевидный момент про порядок, но важно его обозначить. В старых версиях python словарь неупорядочен. 
Поэтому везде по возможности всегда лучше использовать `dataclasses` вместо `raw dict`, и тогда ответ будет детерминирован по своей упорядоченности.
3. Использование дефолтного значения в словаре + обработка None значений из функций стандартной библиотеки.
Что-то вроде get_or() из rust. Много какие функции возвращают None без возбуждения исключения. И js может отобразить
на фронтенде как null или NaN. Везде включаем валидацию таких значений, как правило, на уровне `defalut=` в 
`pydantic` или `dataclasses`. Доп. пример из Django: get() несуществующего объекта из бд рейзит исключение, а 
filter(pk=).first() выдает None. И тот, и тот случай необходимо знать и обрабатывать.

### Вывод

Первое и важное эмпирическое правило из ожиданий от библиотек: читать документацию лучше целиком. Да, не от 
корки до корки, но беглым взглядом лучше осмотреть все разделы. Это бы помогло мне из прошлого в 80% ситуаций.
Второе правило, что заявленное поведение не всегда валидно. Поэтому прежде чем пускать что-то в прод, необходимо
произвести проверки. Готовые бесплатные инструменты - экономия вашего времени, но требуют особенного внимания.
Третье: вывод из ваших публичных интерфейсов должен быть строго обговорен и описан собственными структурами,
чтобы избегать неочевидного недетерминированного поведения. Пользователь должен быть уверен в стабильности вашего 
API.