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
    database_host: str
    database_port: str
    database_name: str
    database_backend: str
    database_username: str
    database_password: str
    table: str = None
    data: object = None
    execution_time: str = None


class ExpiredTokenPurgeTask(Task):
    PARAMETER_CLASS = ExpiredTokenPurgeParameters

    def _run(self):
        with self._get_database() as database:
            # database.execute(f'DELETE FROM {self._parameters.table} WHERE ...')

            database.commit()  # pylint: disable=no-member

    def _get_database(self):
        return Database.from_parameters(
            dict(
                host=self._parameters.database_host,
                port=self._parameters.database_port,
                backend=self._parameters.database_backend,
                name=self._parameters.database_name,
                username=self._parameters.database_username,
                password=self._parameters.database_password
            )
        )
