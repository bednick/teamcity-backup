# -*- coding: utf-8 -*-

""""""

import os.path
import logging

from minio import Minio
from abc import ABCMeta, abstractmethod
from prometheus_client import Info, Counter, Summary
from minio.error import ResponseError, BucketAlreadyOwnedByYou, BucketAlreadyExists

from .utils import log_step

__all__ = [
    'DumpBackupError',
    'IStorageFile',
    'MinioStorage',
]

logger = logging.getLogger(__package__)

info = Info('minio_dump', 'Minio backup information')
failure_minio = Counter('minio_dump_failures', 'Count minio-dump failures')
step_minio = Summary('save_data_to_minio', 'Time save_data_to_minio')


class DumpBackupError(Exception):
    pass


class IStorageFile(metaclass=ABCMeta):

    @abstractmethod
    def save_file(self, filename):
        pass


class MinioStorage(IStorageFile):

    def __init__(self, endpoint: str, access_key: str, secret_key: str, secure: bool, bucket: str):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        self.bucket = bucket

        self.client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)

    @staticmethod
    def _get_name(filename) -> str:
        name, _ = os.path.splitext(os.path.basename(filename))
        return name

    @step_minio.time()
    @failure_minio.count_exceptions()
    @log_step(name='save data to minio', logger=logger)
    def save_file(self, filename):
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except (BucketAlreadyOwnedByYou, BucketAlreadyExists):
            pass
        except ResponseError as e:
            raise DumpBackupError(f'Error check/create bucket: {e}')
        except Exception as e:
            raise DumpBackupError(f'Internal error: {e}')

        name = self._get_name(filename)
        logger.info(f'DUMP bucket: {self.bucket}, name: {name}, filename: {filename}')
        info.info({'backup_bucket': self.bucket, 'backup_name': name, 'backup_filename': filename})
        try:
            self.client.fput_object(
                bucket_name=self.bucket, object_name=name, file_path=filename, content_type='application/zip'
            )
        except ResponseError as e:
            raise DumpBackupError(f'Error put object: {e}')
        except Exception as e:
            raise DumpBackupError(f'Internal error: {e}')
