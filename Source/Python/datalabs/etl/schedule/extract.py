""" Convert a DAG schedule into a list of DAGs to run. """
from   dataclasses import dataclass
from   io import BytesIO
import logging

import pandas
import numpy

from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.etl.dag.state import StatefulDAGMixin
from   datalabs.etl.task import ExecutionTimeMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class ScheduledDAGStateExtractorParameters:
    dag_state: str


class ScheduledDAGStateExtractor(ExecutionTimeMixin, StatefulDAGMixin, Task, CSVReaderMixin, CSVWriterMixin):
    PARAMETER_CLASS = ScheduledDAGStateExtractorParameters

    def run(self):
        dag_runs = None

        dag_runs = pandas.read_csv(BytesIO(self._data[0]))
        LOGGER.info("Dag Runs:\n%s", dag_runs)

        dag_runs_status = self._get_dags(dag_runs)
        LOGGER.info("Dags to Run:\n%s", dag_runs_status)

        return [self._dataframe_to_csv(dag_runs_status, date_format='%Y-%m-%d %H:%M:%S')]

    def _get_dags(self, dag_runs):
        state = self._get_state_plugin(self._parameters)
        dag_runs = dag_runs.fillna(numpy.nan).replace([numpy.nan], [None])

        dag_runs["Status"] = dag_runs.apply(lambda dag: self._get_run_statuses(state, dag), axis = 1)

        dag_runs['Run'] = dag_runs['Run'].astype('datetime64[ns]')

        return dag_runs

    @classmethod
    def _get_run_statuses(cls, state, dag_runs):
        status = None

        if dag_runs["Run"] is not None:
            status = state.get_dag_status(
                dag_runs["DAG"],
                pandas.to_datetime(dag_runs["Run"]).isoformat()
            ).value

        return status
