""" BitBucket synchronization objects. """

from   collections import namedtuple
import logging
import os
from   pathlib import Path
import shutil
import subprocess
import tempfile
from   urllib.parse import urlparse

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


Configuration = namedtuple('Configuration', 'clone_url branch dag_source_path dag_target_path')


class Synchronizer():
    def __init__(self, config: Configuration):
        self._config = config
        clone_url = urlparse(self._config.clone_url)
        clone_path = Path(clone_url.path)

        self._repository_name = clone_path.name.split('.')[0]
        self._project_name = clone_path.parent.name
        LOGGER.debug('BitBucket repository URL: %s', self._config.clone_url)

    def sync(self):
        # import pdb; pdb.set_trace()
        with tempfile.TemporaryDirectory() as temp_directory:
            os.chdir(temp_directory)

            LOGGER.info('-- Cloning --')
            self._clone_repository()

            # os.chdir(Path(temp_directory).joinpath(data.repository))

            LOGGER.info('-- Syncing --')
            self._copy_dags()

        LOGGER.info(
            'Done syncing "%s" branch of repository "%s" under project "%s".',
            self._config.branch, self._repository_name, self._project_name
        )

    def _clone_repository(self):
        command = 'git clone --single-branch -b {} {}'.format(
            self._config.branch, self._config.clone_url
        )

        subprocess.call(command.split(' '))

    def _copy_dags(self):
        shutil.copytree(self._config.dag_source_path, self._config.dag_source_path)
