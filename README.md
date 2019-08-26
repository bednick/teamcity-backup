# Задача
Автоматизировать создание и хранение Teamcity backup. Получать алерты, если backup не сделался.

# Решение
- teamcity_backup — содержит исходный код сервиса. 
- prometheus — содержит настройки [Prometheus](https://prometheus.io/docs/prometheus/latest/configuration/configuration/).

## Переменные окружения
Настройка сервисов происходит по средством определения переменных окружения.


| Name                              | Type    | Required | Default | Description |
|:---------------------------------:|:-------:|:--------:|:-------:|:-----------:|
| BACKUP_PERIODICITY                | integer | False    | 720     | Переодичность создания бекапа (в минутах) |
| SERVICE_PORT                      | integer | False    | 8765    |  |
| SERVICE_LOG_LEVEL                 | string  | False    | "INFO"  | Уровень логирования |
| TEAMCITY_USER                     | string  | True     |         |    |
| TEAMCITY_PASS                     | string  | True     |         |    |
| TEAMCITY_DATADIR                  | string  | False    | "/data/teamcity_server/datadir" |    |
| BACKUP_FILENAME                   | string  | False    |  "auto-backup"  |    |
| BACKUP_ADD_TIMESTAMP              | boolean | False    |  True   |    |
| BACKUP_INCLUDE_CONFIGS            | boolean | False    |  True   |    |
| BACKUP_INCLUDE_DATABASE           | boolean | False    |  True   |    |
| BACKUP_INCLUDE_BUILD_LOGS         | boolean | False    |  True   |    |
| BACKUP_INCLUDE_PERSONAL_CHANGES   | boolean | False    |  True   |    |
| BACKUP_RUNNING_BUILDS             | boolean | False    |  False  |    |
| BACKUP_INCLUDE_SUPPLIMENTARY_DATA | boolean | False    |  False  |    |
| TEAMCITY_HOST                     | string  | True     |         |    |
| TEAMCITY_PORT                     | integer | False    |  8111   |    |
| MINIO_ENDPOINT                    | string  | True     |         |    |
| MINIO_ACCESS_KEY                  | string  | True     |         |    |
| MINIO_SECRET_KEY                  | string  | True     |         |    |
| MINIO_SECURE                      | boolean | False    |  False  |    |
| MINIO_BUCKET                      | string  | False    |  "teamcity-backup"  |    |

## Развертывание
Сервис описан в виде python-пакета. Для запуска необходимо:
1. Установить все необходимые зависимости:
    ```commandline
    python -m pip install -r requirements.txt
    ```
2. Определить все обязательные переменные окружения.
3. Запустить сервис:
    ```commandline
    python -m teamcity_backup
    ```

## Развертывание по средствам docker (docker-compose)
Развертывание предполагается через docker-compose.
Для этого необходимо создать файл с именем `.env` содержащий определения всех обязательных перемен окружения.
В корне проекта лежит файл пример `example.env`.

Для разработки/тестирования можно использовать настройки из `example.env`:
```bash
cat example.env > .env
```

### Первичная настройка
При первичной настройке необходимо настроить teamcity-server, для этого необходмо зайти на
[http://localhost:8111](http://localhost:8111) и при первичной настройки необходимо указать:
1. Путь хранения данных указать равный `TEAMCITY_DATADIR`
(по умолчанию `/data/teamcity_server/datadir` и дополнительной настройки не требует)
2. Произвести регистрацию пользователя с:
    - Именем пользоваля равным переменной окружения `TEAMCITY_USER`
    - Паролем равным переменной окружения `TEAMCITY_PASS`
