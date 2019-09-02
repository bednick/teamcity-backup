# -*- coding: utf-8 -*-

""""""

import os
import time
import logging
import requests

from datetime import datetime
from abc import ABCMeta, abstractmethod
from requests.auth import HTTPBasicAuth
from prometheus_client import Counter, Summary
from requests.exceptions import ConnectTimeout, ReadTimeout, RequestException

from .utils import log_step

__all__ = [
    'CreateTeamcityBackupError',
    'TeamcityBackupTimeout',
    'IBackupFile',
    'TeamcityBackupURL',
]

logger = logging.getLogger(__package__)

failure_url = Counter('backup_url_failures', 'Count backup-url failures')
step_url = Summary('teamcity_backup_url', 'Time teamcity_backup_url')
wait = Summary('wait_backup_file', 'Time wait *.zip file')


class CreateTeamcityBackupError(Exception):
    pass


class TeamcityBackupTimeout(CreateTeamcityBackupError):
    pass


class IBackupFile(metaclass=ABCMeta):

    @abstractmethod
    def create_backup(self) -> str:
        """
        Create backup file
        :return: Path to backup-file
        """
        pass


class TeamcityBackupURL(IBackupFile):

    def __init__(self, tc_host: str, tc_port: int, tc_user: str, tc_pass: str, tc_datadir: str, backup_timeout: int,
                 filename: str, add_timestamp: bool, include_configs: bool, include_database: bool,
                 include_build_logs: bool, include_personal_changes: bool, include_running_builds: bool,
                 include_supplimentary_data: bool):
        self.tc_host = tc_host
        self.tc_port = tc_port
        self.tc_user = tc_user
        self.tc_pass = tc_pass
        self.tc_datadir = tc_datadir
        self.backup_timeout = backup_timeout
        self.filename = filename
        self.add_timestamp = add_timestamp
        self.include_configs = include_configs
        self.include_database = include_database
        self.include_build_logs = include_build_logs
        self.include_personal_changes = include_personal_changes
        self.include_running_builds = include_running_builds
        self.include_supplimentary_data = include_supplimentary_data
        self._validate_args()

    def _validate_args(self):
        backup_directory = self._get_backup_dir()
        if not os.path.isdir(backup_directory):
            raise ValueError(f'Not found backup directory ({backup_directory})')

    def _get_backup_dir(self) -> str:
        return f'{self.tc_datadir}/backup'

    @step_url.time()
    @failure_url.count_exceptions()
    def _send_request(self) -> str:
        try:
            response = requests.post(
                f'http://{self.tc_host}:{self.tc_port}/httpAuth/app/rest/server/backup',
                auth=requests.auth.HTTPBasicAuth(self.tc_user, self.tc_pass),
                params={
                    'fileName': self.filename,
                    'addTimestamp': self.add_timestamp,
                    'includeConfigs': self.include_configs,
                    'includeDatabase': self.include_database,
                    'includeBuildLogs': self.include_build_logs,
                    'includePersonalChanges': self.include_personal_changes,
                    'includeRunningBuilds': self.include_running_builds,
                    'includeSupplimentaryData': self.include_supplimentary_data,
                }
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
    def _wait_backup_file(self, filename: str) -> bool:
        start = datetime.now()

        while not os.path.isfile(filename):  # not os.path.isfile(filename) and os.path.isfile(f'{filename}.part'):
            if self.backup_timeout and (datetime.now() - start).total_seconds() > 60 * self.backup_timeout:
                break
            time.sleep(30)

        return os.path.isfile(filename)

    @log_step(name='create teamcity backup file', logger=logger)
    def create_backup(self) -> str:
        backup_name = self._send_request()

        backup_directory = self._get_backup_dir()
        filename = f'{backup_directory}/{backup_name}'

        if not self._wait_backup_file(filename):
            logger.debug(f'All backups: {os.listdir(backup_directory)}')
            raise TeamcityBackupTimeout(
                f'Teamcity backup timeout {self.backup_timeout} minutes, file {filename} not found'
            )
        return filename
