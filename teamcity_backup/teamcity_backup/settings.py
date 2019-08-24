# -*- coding: utf-8 -*-

"""
    If env not fount raise "envparse.ConfigurationError"
"""

from envparse import env

BACKUP_PERIODICITY = max(1, env.int('BACKUP_PERIODICITY', default=12*60))  # minutes

TEAMCITY_USER = env.str('TEAMCITY_USER')
TEAMCITY_PASS = env.str('TEAMCITY_PASS')
TEAMCITY_DATADIR = env.str('TEAMCITY_DATADIR', default='/data/teamcity_server/datadir')
TEAMCITY_PART_TIMEOUT = max(0, env.int('TEAMCITY_PART_TIMEOUT', default=60))

# ./app/rest/application.wadl
BACKUP_FILENAME = env.str('BACKUP_FILENAME', default='auto-backup')
BACKUP_ADD_TIMESTAMP = env.bool('BACKUP_ADD_TIMESTAMP', default=True)
BACKUP_INCLUDE_CONFIGS = env.bool('BACKUP_INCLUDE_CONFIGS', default=True)
BACKUP_INCLUDE_DATABASE = env.bool('BACKUP_INCLUDE_DATABASE', default=True)
BACKUP_INCLUDE_BUILD_LOGS = env.bool('BACKUP_INCLUDE_BUILD_LOGS', default=True)
BACKUP_INCLUDE_PERSONAL_CHANGES = env.bool('BACKUP_INCLUDE_PERSONAL_CHANGES', default=True)
BACKUP_RUNNING_BUILDS = env.bool('BACKUP_RUNNING_BUILDS', default=False)
BACKUP_INCLUDE_SUPPLIMENTARY_DATA = env.bool('BACKUP_INCLUDE_SUPPLIMENTARY_DATA', default=False)

# TEAMCITY_HOST = env.str('TEAMCITY_HOST', default='localhost')
TEAMCITY_HOST = env.str('TEAMCITY_HOST')
TEAMCITY_PORT = env.int('TEAMCITY_PORT', default=8111)

MINIO_ENDPOINT = env.str('MINIO_ENDPOINT')
MINIO_ACCESS_KEY = env.str('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = env.str('MINIO_SECRET_KEY')
MINIO_SECURE = env.bool('MINIO_SECURE', default=False)
MINIO_BUCKET = env.str('MINIO_BUCKET', default='teamcity-backup')
