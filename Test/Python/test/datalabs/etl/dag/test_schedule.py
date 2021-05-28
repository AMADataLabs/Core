""" Source: datalabs.etl.dag.schedule """
from   datetime import datetime, timedelta
from   io import BytesIO
import json
import logging
from   pathlib import Path
import tempfile

import mock
import pandas
import pytest

from   datalabs.etl.dag.schedule import DAGScheduler, DAGSchedulerParameters
from   datalabs.etl.dag.state.base import Status
from   datalabs.etl.dag.state.file import DAGState

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_getting_state_plugin(scheduler):
    state = scheduler._get_state_plugin()

    assert hasattr(state, 'get_status')
    assert state.get_status('BOGUS_DAG', datetime.now()) == Status.Unknown


def test_dag_flagged_not_started_if_no_state(scheduler):
    state = scheduler._get_state_plugin()
    dag = dict(name='BUGUS_DAG', execution_time=pandas.Timestamp(datetime.now()))

    started = scheduler._is_started(state, dag)

    assert started == False


def test_execution_time_returns_next_execution_time(scheduler, target_execution_time):
    dag = dict(name='BUGUS_DAG', schedule="*/15 * * * *")
    expected_execution_time = target_execution_time.replace(minute=30, second=0, microsecond=0)

    execution_time = scheduler._get_execution_time(target_execution_time, dag)

    assert execution_time == expected_execution_time

def test_execution_time_bounds_are_correct(scheduler, target_execution_time):

    lower_bound, upper_bound = scheduler._get_execution_time_bounds(target_execution_time)

    assert lower_bound.year == target_execution_time.year
    assert lower_bound.month == target_execution_time.month
    assert lower_bound.day == target_execution_time.day
    assert lower_bound.hour == target_execution_time.hour
    assert lower_bound.minute == 30
    assert lower_bound.second == 0
    assert lower_bound.microsecond == 0

    assert upper_bound.year == target_execution_time.year
    assert upper_bound.month == target_execution_time.month
    assert upper_bound.day == target_execution_time.day
    assert upper_bound.hour == target_execution_time.hour
    assert upper_bound.minute == 45
    assert upper_bound.second == 0
    assert upper_bound.microsecond == 0


def test_execution_times_are_calculated_correctly(scheduler, schedule, base_time):
    expected_execution_times = [
        datetime(2021, 5, 10, 15, 15, 0),
        datetime(2021, 5, 10, 15, 10, 0),
        datetime(2021, 5, 12, 0, 5, 0)
    ]

    execution_times = scheduler._get_execution_times(schedule, base_time)

    for execution_time,expected_execution_time in zip(execution_times,expected_execution_times):
        assert execution_time.to_pydatetime() == expected_execution_time


def test_scheduled_dags_are_correctly_identified(scheduler, schedule, base_time):
    schedule["execution_time"] = scheduler._get_execution_times(schedule, base_time)

    scheduled_dags = scheduler._get_scheduled_dags(schedule, base_time)

    assert len(scheduled_dags) == 3
    assert scheduled_dags[0] == True
    assert scheduled_dags[1] == False
    assert scheduled_dags[2] == False


def test_started_dags_are_correctly_identified(parameters, schedule, base_time):
    scheduler = DAGScheduler(parameters)
    schedule["execution_time"] = scheduler._get_execution_times(schedule, base_time)
    state = DAGState(dict(BASE_PATH=parameters["BASE_PATH"]))

    state.set_status('archive_cat_photos', schedule.execution_time[0].to_pydatetime(), Status.Pending)

    started_dags = scheduler._get_started_dags(schedule)

    assert len(started_dags) == 3
    assert started_dags[0] == True
    assert started_dags[1] == False
    assert started_dags[2] == False


def test_dags_to_run_are_correctly_identified(parameters, schedule, target_execution_time):
    scheduler = DAGScheduler(parameters)
    execution_times = scheduler._get_execution_times(schedule, target_execution_time - timedelta(minutes=15))
    state = DAGState(dict(BASE_PATH=parameters["BASE_PATH"]))

    dags_to_run = scheduler._determine_dags_to_run(schedule, target_execution_time)

    assert len(dags_to_run) == 1
    assert dags_to_run.name[0] == 'archive_cat_photos'

    state.set_status('archive_cat_photos', execution_times[0].to_pydatetime(), Status.Pending)

    dags_to_run = scheduler._determine_dags_to_run(schedule, target_execution_time)

    assert len(dags_to_run) == 0


def test_dags_to_run_are_transformed_to_csv_bytes(parameters, schedule_csv, target_execution_time):
    parameters["data"] = [schedule_csv.encode('utf-8', errors='backslashreplace')]
    scheduler = DAGScheduler(parameters)

    with mock.patch('datalabs.etl.dag.schedule.DAGScheduler._get_target_execution_time') as get_target_execution_time:
        get_target_execution_time.return_value = target_execution_time

        dags_to_run = scheduler._transform()

    assert len(dags_to_run) == 1
    dag_data = json.loads(dags_to_run[0].decode('utf8'))


@pytest.fixture
def state_directory():
    with tempfile.TemporaryDirectory() as directory:
        yield directory


@pytest.fixture
def parameters(state_directory):
    return dict(
        INTERVAL_MINUTES='15',
        STATE_CLASS='datalabs.etl.dag.state.file.DAGState',
        BASE_PATH=state_directory
    )


@pytest.fixture
def scheduler(parameters):
    return DAGScheduler(parameters)


@pytest.fixture
def target_execution_time():
    return datetime(2021, 5, 10, 15, 20, 25)


@pytest.fixture
def base_time(target_execution_time):
    return target_execution_time - timedelta(minutes=15)


@pytest.fixture
def schedule_csv():
    return """name,schedule
archive_cat_photos,15 * */1 * 1
translate_meows,10 */5 * * 1-5
scrape_ama_fan_pages,5 * */1 * 3
"""


@pytest.fixture
def schedule(schedule_csv):
    return pandas.read_csv(BytesIO(schedule_csv.encode('utf8')))
