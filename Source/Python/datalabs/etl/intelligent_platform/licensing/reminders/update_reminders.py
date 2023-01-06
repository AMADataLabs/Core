""" Task classes for updating the group reminders. """
from   dataclasses import dataclass
import logging

from   datalabs.access.orm import Database
from   datalabs.parameter import add_schema
from   datalabs.task import Task

from Source.Python.datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=too-many-instance-attributes
@add_schema
@dataclass
class UpdateRemindersParameters:
    execution_time: str = None


class UpdateRemindersTask(CSVReaderMixin, CSVWriterMixin, Task):

    PARAMETER_CLASS = UpdateRemindersParameters

    def run(self):

        group_info = self._csv_to_dataframe(self._data[0])[['id', 'renewal_reminders']].drop_duplicates()
        group_info.loc[0:group_info.shape[0], ['renewal_reminders']] += 1

        return [self._dataframe_to_csv(group_info)]
