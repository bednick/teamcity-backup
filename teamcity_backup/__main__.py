# -*- coding: utf-8 -*-

""""""

import time
import logging
import schedule

from prometheus_client import start_http_server, Counter, Gauge

from teamcity_backup.settings import BACKUP_PERIODICITY, SERVICE_PORT, SERVICE_LOG_LEVEL
from teamcity_backup.backup import CreateTeamcityBackupError, DumpBackupError, teamcity_backup_url, save_data_to_minio

logger = logging.getLogger(__package__)

g = Gauge('backup_task', 'Gauge backup-task')
failure = Counter('backup_task_failures', 'Count backup failures')


@g.track_inprogress()
def task():
    try:
        with failure.count_exceptions():
            logger.debug('Start backup')
            logger.info(f'Start teamcity backup...')
            name = teamcity_backup_url()
            logger.info(f'Created backup: {name}')
            logger.info('Start save data to minio...')
            save_data_to_minio(name)
            logger.info('Saved data to minio')
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

    start_http_server(port=SERVICE_PORT)
    logger.debug(f'START HTTP SERVER. PORT: {SERVICE_PORT}')

    schedule.every(BACKUP_PERIODICITY).minutes.do(task)
    while True:
        schedule.run_pending()
        # check task every 30 seconds
        time.sleep(30)
