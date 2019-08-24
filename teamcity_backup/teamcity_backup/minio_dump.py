# -*- coding: utf-8 -*-

""""""

import os
import time
import logging

from minio import Minio
from typing import Optional
from datetime import datetime
from minio.error import ResponseError, BucketAlreadyOwnedByYou, BucketAlreadyExists

from .settings import (
    MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_SECURE, MINIO_BUCKET, TEAMCITY_DATADIR,
    TEAMCITY_PART_TIMEOUT
)

__all__ = [
    'DumpBackupError',
    'save_data_to_minio',
]

logger = logging.getLogger(__package__)


client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=MINIO_SECURE)


class DumpBackupError(Exception):
    pass


def wait_part(filename: str, max_timeout: Optional[int]) -> bool:
    start = datetime.now()
    while not os.path.isfile(filename) and os.path.isfile(f'{filename}.part'):
        if max_timeout and (datetime.now() - start).total_seconds() > max_timeout:
            break
        time.sleep(5)

    return os.path.isfile(filename)


def save_data_to_minio(name: str):
    try:
        if not client.bucket_exists(MINIO_BUCKET):
            client.make_bucket(MINIO_BUCKET)
    except (BucketAlreadyOwnedByYou, BucketAlreadyExists):
        pass
    except ResponseError as e:
        raise DumpBackupError(f'Error check/create bucket: {e}')
    except Exception as e:
        raise DumpBackupError(f'Internal error: {e}')
    else:
        directory = f'{TEAMCITY_DATADIR}/backup'
        if os.path.isdir(directory):
            logger.debug(f'ALL BACKUPS: {os.listdir(directory)}')
        else:
            raise DumpBackupError(f'Not found dir: {directory}')

        filename = f'{directory}/{name}'
        logger.info(f'WAIT PART {TEAMCITY_PART_TIMEOUT}: {filename}')

        if not wait_part(filename, TEAMCITY_PART_TIMEOUT):
            raise DumpBackupError(f'Teamcity part timeout {TEAMCITY_PART_TIMEOUT} seconds')

        logger.info(f'DUMP bucket: {MINIO_BUCKET}, name: {name}, filename: {filename}')
        try:
            client.fput_object(MINIO_BUCKET, name, filename, content_type='application/zip')
        except ResponseError as e:
            raise DumpBackupError(f'Error put object: {e}')
        except Exception as e:
            raise DumpBackupError(f'Internal error: {e}')
