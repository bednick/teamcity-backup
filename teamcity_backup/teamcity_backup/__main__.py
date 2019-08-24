# -*- coding: utf-8 -*-

""""""

import time
import logging
import schedule

from teamcity_backup.settings import BACKUP_PERIODICITY
from teamcity_backup.backup_url import create_teamcity_backup, CreateTeamcityBackupError
from teamcity_backup.minio_dump import save_data_to_minio, DumpBackupError

logger = logging.getLogger(__package__)


def task():
    logger.debug('Start backup')
    try:
        logger.info(f'Start teamcity backup...')
        filename = create_teamcity_backup()
        logger.info(f'Created backup: {filename}')
        save_data_to_minio(filename)
        logger.info(f'Saved data to minio')
    except CreateTeamcityBackupError as e:
        logger.exception(f'Error create backup: {e}', exc_info=e)
    except DumpBackupError as e:
        logger.exception(f'Error save to minio: {e}', exc_info=e)


if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('[%(asctime)-15s] [%(levelname)-8s] %(message)s'))
    logger.addHandler(ch)

    schedule.every(BACKUP_PERIODICITY).minutes.do(task)
    while True:
        schedule.run_pending()
        # check task every 30 seconds
        time.sleep(30)
