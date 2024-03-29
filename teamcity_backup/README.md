## Переменные окружения
Настройка сервисов происходит по средством определения переменных окружения.

| Name                              | Type    | Required | Default | Description |
|:---------------------------------:|:-------:|:--------:|:-------:|:------------|
| BACKUP_PERIODICITY                | integer | False    | 720     | Переодичность создания backup (в минутах) |
| SERVICE_PORT                      | integer | False    | 8765    | Порт на котором развернут teamcity_backup сервис. <br/>Метрики доступны на `SERVICE_HOST:${SERVICE_PORT}/metrics` |
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
| TEAMCITY_HOST                     | string  | True     |         | Хост teamcity сервера |
| TEAMCITY_PORT                     | integer | False    | 8111    | Порт на котором развернут teamcity сервера |
| MINIO_ACCESS_KEY                  | string  | True     |         | Ключ доступа длиной не менее 3 символов |
| MINIO_SECRET_KEY                  | string  | True     |         | Секретный ключ длиной не менее 8 символов |
| MINIO_SECURE                      | boolean | False    | False   | Будет ли использоваться https:// при работе с minio |
| MINIO_BUCKET                      | string  | False    | teamcity-backup | Minio bucket в котором будут сохраняться backup'ы teamcity |
| GF_SECURITY_ADMIN_USER            | string  | False    | admin   | Логин админ пользователя grafana |
| GF_SECURITY_ADMIN_PASSWORD        | string  | False    | admin   | Пароль админ пользователя grafana |



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
