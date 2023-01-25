""" Task classes for managing developer user tokens. """
from   dataclasses import dataclass
import logging

from   datalabs.access.orm import Database
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=too-many-instance-attributes
@add_schema
@dataclass
class ExpiredTokenPurgeParameters:
    backend: str
    host: str
    port: str
    username: str
    password: str
    database: str
    execution_time: str = None


class ExpiredTokenPurgeTask(Task):
    PARAMETER_CLASS = ExpiredTokenPurgeParameters

    def run(self):
        with self._get_database() as database:
            database.execute(f'DELETE FROM {self._parameters.database}.Tokens WHERE expiry_time < now()')
            database.commit()  # pylint: disable=no-member

    def _get_database(self):
        return Database(
            dict(
                host=self._parameters.host,
                port=self._parameters.port,
                backend=self._parameters.backend,
                name=self._parameters.database,
                username=self._parameters.username,
                password=self._parameters.password
            )
        )
