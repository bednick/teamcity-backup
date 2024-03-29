# Задача
Автоматизировать создание и хранение Teamcity backup. Получать алерты, если backup не сделался.

# Решение
- teamcity_backup — содержит исходный код сервиса. 
- prometheus — содержит настройки [Prometheus](https://prometheus.io/docs/prometheus/latest/configuration/configuration/).
- grafana — содержит настройки [Grafana](https://grafana.com/docs/).

## Переменные окружения
Настройка сервисов происходит по средством определения переменных окружения.

| Name                              | Type    | Required | Default | Description |
|:---------------------------------:|:-------:|:--------:|:-------:|:------------|
| BACKUP_PERIODICITY                | integer | False    | 720     | Переодичность создания backup (в минутах) |
| SERVICE_LOG_LEVEL                 | string  | False    | INFO    | Уровень логирования сервиса teamcity_backup |
| TEAMCITY_USER                     | string  | True     |         | Логин пользователя teamcity с помощью которого будет происходить создание backup'ов |
| TEAMCITY_PASS                     | string  | True     |         | Пароль пользователя teamcity с помощью которого будет происходить создание backup'ов  |
| TEAMCITY_DATADIR                  | string  | False    | /data/teamcity_server/datadir | Место хранения данных teamcity. <br/>Директория хранения backup'ов: `${TEAMCITY_DATADIR}/backup` |
| TEAMCITY_BACKUP_TIMEOUT           | integer | False    | 60      | Время ожидания создания файла `backup_name.zip` (в минутах). Если значение равно 0, то время ожидания неограниченно.<br/>**ВАЖНО**: значение 0 является нерекомендуемым для prod использования, так-как может вызвать бесконечное зависание! |
| BACKUP_FILENAME                   | string  | False    | auto-backup    | Аргумент [fileName](https://www.jetbrains.com/help/teamcity/rest-api.html#RESTAPI-DataBackup) |
| BACKUP_ADD_TIMESTAMP              | boolean | False    | True    | Аргумент [addTimestamp](https://www.jetbrains.com/help/teamcity/rest-api.html#RESTAPI-DataBackup) |
| BACKUP_INCLUDE_CONFIGS            | boolean | False    | True    | Аргумент [includeConfigs](https://www.jetbrains.com/help/teamcity/rest-api.html#RESTAPI-DataBackup) |
| BACKUP_INCLUDE_DATABASE           | boolean | False    | True    | Аргумент [includeDatabase](https://www.jetbrains.com/help/teamcity/rest-api.html#RESTAPI-DataBackup) |
| BACKUP_INCLUDE_BUILD_LOGS         | boolean | False    | True    | Аргумент [includeBuildLogs](https://www.jetbrains.com/help/teamcity/rest-api.html#RESTAPI-DataBackup) |
| BACKUP_INCLUDE_PERSONAL_CHANGES   | boolean | False    | True    | Аргумент [includePersonalChanges](https://www.jetbrains.com/help/teamcity/rest-api.html#RESTAPI-DataBackup) |
| BACKUP_RUNNING_BUILDS             | boolean | False    | False   | Аргумент [includeRunningBuilds](https://www.jetbrains.com/help/teamcity/rest-api.html#RESTAPI-DataBackup) |
| BACKUP_INCLUDE_SUPPLIMENTARY_DATA | boolean | False    | False   | Аргумент [includeSupplimentaryData](https://www.jetbrains.com/help/teamcity/rest-api.html#RESTAPI-DataBackup) |
| MINIO_ACCESS_KEY                  | string  | True     |         | Ключ доступа длиной не менее 3 символов |
| MINIO_SECRET_KEY                  | string  | True     |         | Секретный ключ длиной не менее 8 символов |
| MINIO_BUCKET                      | string  | False    | teamcity-backup | Minio bucket в котором будут сохраняться backup'ы teamcity |
| GF_SECURITY_ADMIN_USER            | string  | False    | admin   | Логин админ пользователя grafana |
| GF_SECURITY_ADMIN_PASSWORD        | string  | False    | admin   | Пароль админ пользователя grafana |

## Развертывание по средствам docker (docker-compose)
Развертывание предполагается через docker-compose.
Для этого необходимо создать файл с именем `.env` содержащий определения всех обязательных перемен окружения.
В корне проекта лежит файл необходимый для минимальной настройки сервисов `start.env`.
Необходимо выполнить:
```bash
cat start.env > .env
```
И заполнить значение переменных с зависимости с ограничениями описанными выше 

В корне проекта также лежит файл пример `example.env`.
Для разработки/тестирования можно использовать его:
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

## Тестирование

### prometheus
Для проверки алертов prometheus используется [UNIT TESTING FOR RULES](https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/).
Файл prometheus/alert.rules.test.yml. Для запуска тестов необходимо выполнить следующую команду:
```bash
docker run -v $PROJECT/prometheus:/tmp --entrypoint "/bin/promtool" prom/prometheus:v2.12.0 test rules /tmp/alert.rules.test.yml
```
Где `$PROJECT` Полный путь до проекта. Например:
```bash
docker run -v d:/teamcity-backup/prometheus:/tmp --entrypoint "/bin/promtool" prom/prometheus:v2.12.0 test rules /tmp/alert.rules.test.yml
```
