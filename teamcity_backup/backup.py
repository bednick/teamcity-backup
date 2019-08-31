# -*- coding: utf-8 -*-

""""""

import os
import time
import logging
import requests

from minio import Minio
from typing import Optional
from datetime import datetime
from requests.auth import HTTPBasicAuth
from prometheus_client import Counter, Summary, Info
from requests.exceptions import ConnectTimeout, ReadTimeout, RequestException
from minio.error import ResponseError, BucketAlreadyOwnedByYou, BucketAlreadyExists

from .settings import *

__all__ = [
    'CreateTeamcityBackupError',
    'DumpBackupError',
    'teamcity_backup_url',
    'save_data_to_minio',
]

logger = logging.getLogger(__package__)

failure_url = Counter('backup_url_failures', 'Count backup-url failures')
step_url = Summary('teamcity_backup_url', 'Time teamcity_backup_url')

failure_minio = Counter('minio_dump_failures', 'Count minio-dump failures')
step_minio = Summary('save_data_to_minio', 'Time save_data_to_minio')
info = Info('minio_dump', 'Minio backup information')
wait = Summary('wait_backup_file', 'Time wait *.zip file')

client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=MINIO_SECURE)


TEAMCITY_BACKUP_URL = f'http://{TEAMCITY_HOST}:{TEAMCITY_PORT}/httpAuth/app/rest/server/backup'
TEAMCITY_BACKUP_PARAMS = {
    'fileName': BACKUP_FILENAME,
    'addTimestamp': BACKUP_ADD_TIMESTAMP,
    'includeConfigs': BACKUP_INCLUDE_CONFIGS,
    'includeDatabase': BACKUP_INCLUDE_DATABASE,
    'includeBuildLogs': BACKUP_INCLUDE_BUILD_LOGS,
    'includePersonalChanges': BACKUP_INCLUDE_PERSONAL_CHANGES,
    'includeRunningBuilds': BACKUP_RUNNING_BUILDS,
    'includeSupplimentaryData': BACKUP_INCLUDE_SUPPLIMENTARY_DATA,
}


class CreateTeamcityBackupError(Exception):
    pass


class DumpBackupError(Exception):
    pass


@step_url.time()
@failure_url.count_exceptions()
def teamcity_backup_url() -> str:
    try:
        response = requests.post(
            TEAMCITY_BACKUP_URL,
            auth=requests.auth.HTTPBasicAuth(TEAMCITY_USER, TEAMCITY_PASS),
            params=TEAMCITY_BACKUP_PARAMS
        )
    except ConnectTimeout as e:
        # Requests that produced this error are safe to retry
        raise CreateTeamcityBackupError(f'Connect timeout: {e}')
    except ReadTimeout as e:
        raise CreateTeamcityBackupError(f'Read timeout: {e}')
    except RequestException as e:
        raise CreateTeamcityBackupError(f'Error request: {e}')
    except Exception as e:
        raise CreateTeamcityBackupError(f'Internal error')

    if response.status_code != 200:
        raise CreateTeamcityBackupError(f'Error status code: {response.status_code}, {response.text}')

    return response.text


@wait.time()
def wait_backup_file(filename: str, max_timeout: Optional[int]) -> bool:
    start = datetime.now()
    # while not os.path.isfile(filename) and os.path.isfile(f'{filename}.part'):
    while not os.path.isfile(filename):
        if max_timeout and (datetime.now() - start).total_seconds() > 60*max_timeout:
            break
        time.sleep(30)

    return os.path.isfile(filename)


@step_minio.time()
@failure_minio.count_exceptions()
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
        logger.info(f'WAIT BACKUP-FILE {TEAMCITY_BACKUP_TIMEOUT}: {filename}')

        if not wait_backup_file(filename, TEAMCITY_BACKUP_TIMEOUT):
            raise DumpBackupError(
                f'Teamcity backup timeout {TEAMCITY_BACKUP_TIMEOUT} minutes, file {filename} not found.'
                f' All backups: {os.listdir(directory)}'
            )

        logger.info(f'DUMP bucket: {MINIO_BUCKET}, name: {name}, filename: {filename}')
        info.info({'backup_bucket': MINIO_BUCKET, 'backup_name': name, 'backup_filename': filename})
        try:
            client.fput_object(MINIO_BUCKET, name, filename, content_type='application/zip')
        except ResponseError as e:
            raise DumpBackupError(f'Error put object: {e}')
        except Exception as e:
            raise DumpBackupError(f'Internal error: {e}')
