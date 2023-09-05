## Simple Task Manager app


Приложение для управления задачами с использованием фреймворков Django, Django Rest Framework.
Основные модели
 - Role
 - User
 - Task

Приложение позволяет создавать, обновлять, удалять задачи и назначать их другим пользователям в системе. 
Пользователи могут иметь несколько ролей, по умолчанию их 3: Admin, Operator и Manager.
Задачи имеют статус, планируемую дату завершения, описание и пользователся на кого она назначена.
Все методы взаимодействия требуют авторизации. Авторизации осуществляется с помощью [simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/),
который работает с парой access и refresh токенов.

Администратор может просматривать, обновлять, удалять все задачи, пользователей, и роли. 
Обычные пользователи могут обновлять свои данные и изменять свои или назначенные им задачи.
В рамках этого приложения не было исплоьзовано отдельная модель Permissions, учитывая размер приложения и достаточности проверок по ролям. 

В качестве СУБД использовался PostgreSQL, для отложенных задач асинхронные таски Celery.
Вся основная функциональность покрыта тестами.

#### Основные эндпоинты

Получение пары токенов, авторизация(POST):
```
http://127.0.0.1:8000/api/token/
```

Обновление токена(POST):
```
http://127.0.0.1:8000/api/token/refresh/
```

Создание пользователя, получение списка пользователей(GET, POST):
```
http://127.0.0.1:8000/api/users/
```

Управление, получение пользхователя по id(GET, POST, DELETE):
```
http://127.0.0.1:8000/api/users/{id}/
```

Создание роли, получение списка ролей(GET, POST):
```
http://127.0.0.1:8000/api/roles/
```

Управление, получение роли по id(GET, POST, DELETE):
```
http://127.0.0.1:8000/api/roles/{id}/
```

Создание задачи, получение списка задач(GET, POST):
```
http://127.0.0.1:8000/api/tasks/
```

Получение, изменение и удаление задачи с соответствующими методами(GET, POST, DELETE):
```
http://127.0.0.1:8000/api/tasks/{id}/
```

#### Фильтрация списка задач

Фильтрация возможна по статусу, названию и по диапазону планируемой даты завершения задачи. Пример
запроса фильтрации приведён ниже. Фильтр - **due_date** выведет все задачи с соответствующей датой завершения,
**due_date_from** и **due_date_to** позволяют указать промежкуток времени.
```
http://127.0.0.1:8000/api/tasks?status=I&due_date_from=2022-12-12
```
Запрос выведет все задачи с заданным статусом и с указанной датой завершения.

Реализована сборка докер образа и Makefile для make команд. Также есть конфигурация pre-commit хуков, в котором isort, black, flake8 и autoflake.

#### 1. Build
```
make build
```

#### 2. Start services
```
make up
```

#### 3. Set up DB
```
make build_db
```

#### 4. Run tests
```
make test
```
