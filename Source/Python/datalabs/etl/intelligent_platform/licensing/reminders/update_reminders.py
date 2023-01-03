""" Task classes for updating the group reminders. """
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
class UpdateRemindersParameters:
    backend: str
    host: str
    port: str
    username: str
    password: str
    database: str
    table: str = None
    execution_time: str = None


class UpdateRemindersTask(Task):
    PARAMETER_CLASS = UpdateRemindersParameters

    def _run(self):
        with self._get_database() as database:
            database.execute(f'SELECT g.id, g.renewal_reminders FROM usermgmt.Groups g '
                             f'WHERE TIMESTAMPDIFF(MONTH, g.valid_from, current_date()) = 11 '
                             f'AND g.renewal_reminders  = 0 order by g.id')
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
