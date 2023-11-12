### 1 пример
Модуль:

https://github.com/Roman-AlexeevP/GameOfTODO/tree/master/src/db 

В данном модуле использована простая абстракция на уровне 

"Класс в приложении" -> "Класс менеджер с логикой запросов"-> "Драйвер БД".

Сейчас бы я изменил взаимодействие с БД и взял бы ОРМ sqlAlchemy, например,
чтобы усилия направленные на работу с драйвером базы данных и маппингом класса
в модель БД исполняла ОРМ. Очевидно, что невозможно достичь соответствия 1 к 1 
модели АТД и модели в базе данных, поэтому был бы добавлен адаптер. А к ним уже
соответственно датаклассы как классы-хранилища, получающиеся из инстанса АТД, для
взаимодействия с конкретными модулями (интерфейс, логика расчета опыта)
Тогда бы цепочка была: 

БД -> ОРМ -> Адаптеры -> АТД -> датаклассы в конкретные модули.

### 2 пример

В одном из созданных мной АПИ есть подобная структура модулей и папок:

- apis
  - api1
    - views
    - services
    - utils
    - models
  - api2
    - ...
    - ...
    - ...
- config
  - config.py
- routes
  - views
- main.py
- tasks.py

В данном случае, в рамках размера АПИ (он средний) можно было упростить убрал излишнее разделение по папкам
api1, api2. Хоть и задумывалось это как уровень разных мини-приложений, они все равно связаны и поэтому
импорт в соседний модуль выглядит монструзно и путает разработчика.
Я бы выделил такую структуру:
- api1
  - tasks
  - models
  - views
  - services
- api2
  - tasks
  - models
  - views
  - services
- config
- routes
- main.py

Таким образом уровень вложенности станет <=2 и уже тогда работа с проектом станет проще,
лаконичнее. Проблем с импортами станет меньше, когнитивная нагрузка на мозг человека, который знакомится с апи тоже.


## Вывод

В основном нелокальные изменения в проектах это то, что постепенно разрослось из мелкого 
упущения дизайна и стало большим якорем и не меняется из-за большой связности модулей.
В моих примерах в основном используется какое-либо упрощение, потому что только окинув взглядом проект целиком
после какого-либо времени работы с ним, мы можем понять какой интерфейс не так удобен, где провисает связность и тд.
Также, когда ты принимаешь возможность каких-либо изменений в проекте, то становится проще работать,
ты не ощущаешь себя заложником одного модуля и не боишься изменений.