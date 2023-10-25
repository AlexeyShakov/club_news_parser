# Парсинг футбольных новостей

## Описание проекта
Данный проект является чисто учебным и имеет ряд недочетов, как дублирование кода, например. Его целью является практика 
новых технологий, в данном случае реализация различных вариантов общения между микросервисами. Проект состоит из трех микросервисов: 
парсер(данный проект), сервис переводов(https://github.com/AlexeyShakov/translatiion_service) и сервис, который публикует 
контент в телеграм(https://github.com/AlexeyShakov/telegram_service).

## Описание работы сервиса
1. Новости о футбольных командах парсятся с определенного сайта. Происходит обработка html-страниц и преобразование их в
python-объекты. Объекты после парсинга сохраняются в базу и отправляются дальше на сервис переводов.
2. Данные посылаются на внешний API(яндекс переводчик). После этого данные посылаются на сервис, которые шлет новости в группу
в телеграме.
3. Данные посылаются в группу в телеграмме.

В качестве "доставщика" сообщений между сервисами может использоваться одна из следующих технологий: REST API, GRPC, 
брокер сообщений.

Также в сервисе парсера есть две фоновые задачи, функции которых в следующем:
* обработка новостей с ошибками - повторная отправка новостей на соответствующие сервисы;
* удаление старых новостей, которые опубликованы в телеграм.

## Используемые технологии
* aiohttp - в качестве асинхронного клиента для посылки данных на другие сервисы;
* grpc - для посылки данных на другие микросервисы;
* брокер сообщений - для посылки данных на другие микросервисы;
* beautifulsoup4 - для парсинга новостей;
* sqlalchemy и alembic - для взаимодействие с SQL БД(PostgreSQL);
* requests - синхронный клиент для посылки данных;
* multithreading - для реализации фоновых задач;
* asyncio - для реализации асинхронной логики.

## Зависимости
См. файл requirements.txt.

В процессе работы сервисов используется стороннее API(яндекс переводчик) для перевода новостей.
Для работы c переводчиком нужно зарегистрироваться и получить специальный токен. Этот токен должен лежать в
.env-файле в сервисе переводов https://github.com/AlexeyShakov/translatiion_service. Инструкция по получению токена:
https://cloud.yandex.ru/docs/translate/operations/

## Структура проекта
- logs
- migrations
- services
    - grpc_translations
      - app
      - build
      - setup.py
      ...
    - telegram_service
      - src
      - main.py
      ...
    - translatiion_service
        - src
        - main.py
        ...
- src
- .gitignore
- main.py
- .env
...


## Структура .env
DB_PORT=<порт для postgres-сервера>

DB_HOST=localhost

POSTGRES_DB=<название базы данных>

POSTGRES_USER=<юзернэйм пользователя БД>

POSTGRES_PASSWORD=<пароль от БД>

TRANSLATION_PORT=<Порт сервиса переводов в случае HTTP общения между сервисами>
TRANSLATION_CONTAINER=translation_app

TELEGRAM_PORT=<Порт сервиса телеграма в случае HTTP общения между сервисами>
TELEGRAM_CONTAINER=telegram_app

OVER_HTTP= 0 или 1 - указатель того, что используется REST API для общения между сервисами

OVER_GRPC= 0 или 1 - указатель того, что используется GRPC для общения между сервисами

OVER_QUEUE= 0 или 1 - указатель того, что используется брокер сообщений для общения между сервисами

GRPC_TRANSLATION_PORT=<порт, на котором запущен grpc-сервер сервиса переводов>

GRPC_TELEGRAM_PORT=<порт, на котором запущен grpc-сервер сервиса публикации новостей в телеграмм>

## Разворачивание проекта
