# -*- coding: utf-8 -*-

""""""

import os
import re
import codecs
import setuptools

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


class CleanCommand(setuptools.Command):
    """
    Custom clean command to tidy up the project root.
    """
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    # noinspection PyMethodMayBeStatic
    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')


setuptools.setup(
    name='teamcity_backup',

    python_requires='==3.7.*',

    version=find_version('teamcity_backup', '__init__.py'),

    author='Bedarev Nickolay',
    author_email='nikolay.bedarev@yandex.ru',
    description='',

    install_requires=[
        'requests>=2.21.0',
        'prometheus_client>=0.7.1',
        'schedule>=0.6.0',
        'envparse>=0.2.0',
        'minio>=3.0.1',
    ],

    packages=setuptools.find_packages(exclude=('tests', )),

    classifiers=['Private :: Do Not Upload'],

    cmdclass={
        'clean': CleanCommand,
    }
)
