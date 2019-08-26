# -*- coding: utf-8 -*-

""""""

import requests

from requests.auth import HTTPBasicAuth
from prometheus_client import Counter, Summary
from requests.exceptions import ConnectTimeout, ReadTimeout, RequestException

from .settings import (
    TEAMCITY_HOST, TEAMCITY_PORT,
    TEAMCITY_USER, TEAMCITY_PASS,
    BACKUP_FILENAME, BACKUP_ADD_TIMESTAMP, BACKUP_INCLUDE_CONFIGS, BACKUP_INCLUDE_DATABASE, BACKUP_INCLUDE_BUILD_LOGS,
    BACKUP_INCLUDE_PERSONAL_CHANGES, BACKUP_RUNNING_BUILDS, BACKUP_INCLUDE_SUPPLIMENTARY_DATA
)

__all__ = [
    'CreateTeamcityBackupError',
    'teamcity_backup_url',
]

failure = Counter('backup_url_failures', 'Count backup-url failures')
step = Summary('teamcity_backup_url', 'Time teamcity_backup_url')

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


@step.time()
@failure.count_exceptions()
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
