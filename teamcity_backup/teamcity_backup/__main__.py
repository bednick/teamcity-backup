# -*- coding: utf-8 -*-

""""""

import time
import logging
import schedule

from functools import partial
from prometheus_client import start_http_server, Counter, Gauge

from teamcity_backup.backup import *
from teamcity_backup.settings import *
from teamcity_backup.storage import *

logger = logging.getLogger(__package__)

g = Gauge('backup_task', 'Gauge backup-task')
failure = Counter('backup_task_failures', 'Count backup failures')


@g.track_inprogress()
def task(backup: IBackupFile, storage: IStorageFile):
    try:
        with failure.count_exceptions():
            filename = backup.create_backup()
            storage.save_file(filename)
    except CreateTeamcityBackupError as e:
        logger.exception(f'Error create backup: {e}', exc_info=e)
    except DumpBackupError as e:
        logger.exception(f'Error save to minio: {e}', exc_info=e)
    except Exception as e:
        logger.exception('Internal error', exc_info=e)


if __name__ == '__main__':
    logger.setLevel(SERVICE_LOG_LEVEL)
    ch = logging.StreamHandler()
    ch.setLevel(SERVICE_LOG_LEVEL)
    ch.setFormatter(logging.Formatter('[%(asctime)-15s] [%(levelname)-8s] %(message)s'))
    logger.addHandler(ch)

    backup_url = TeamcityBackupURL(
        tc_host=TEAMCITY_HOST,
        tc_port=TEAMCITY_PORT,
        tc_user=TEAMCITY_USER,
        tc_pass=TEAMCITY_PASS,
        tc_datadir=TEAMCITY_DATADIR,
        backup_timeout=TEAMCITY_BACKUP_TIMEOUT,
        filename=BACKUP_FILENAME,
        add_timestamp=BACKUP_ADD_TIMESTAMP,
        include_configs=BACKUP_INCLUDE_CONFIGS,
        include_database=BACKUP_INCLUDE_DATABASE,
        include_build_logs=BACKUP_INCLUDE_BUILD_LOGS,
        include_personal_changes=BACKUP_INCLUDE_PERSONAL_CHANGES,
        include_running_builds=BACKUP_RUNNING_BUILDS,
        include_supplimentary_data=BACKUP_INCLUDE_SUPPLIMENTARY_DATA,
    )

    storage_minio = MinioStorage(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE,
        bucket=MINIO_BUCKET,
    )

    start_http_server(port=SERVICE_PORT)
    logger.debug(f'START HTTP SERVER. PORT: {SERVICE_PORT}')

    schedule.every(BACKUP_PERIODICITY).minutes.do(partial(task, backup=backup_url, storage=storage_minio))
    while True:
        schedule.run_pending()
        # check task every 30 seconds
        time.sleep(30)
