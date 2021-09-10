""" Source: datalabs.etl.dag.schedule.task """
from   datetime import datetime, timedelta
from   io import BytesIO
import json
import logging
import pickle
import tempfile

import mock
import pandas
import pytest

from   datalabs.etl.dag.schedule.task import DAGSchedulerTask
from   datalabs.etl.dag.state.base import Status
from   datalabs.etl.dag.state.file import DAGState

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_getting_state_plugin(scheduler):
    state = scheduler._get_state_plugin()

    assert state.get_dag_status('BOGUS_DAG', datetime.utcnow().isoformat()) == Status.UNKNOWN


# pylint: disable=redefined-outer-name, protected-access
def test_dag_flagged_not_started_if_no_state(scheduler):
    state = scheduler._get_state_plugin()
    dag = dict(name='BUGUS_DAG', execution_time=pandas.Timestamp(datetime.utcnow()))

    assert not scheduler._is_started(state, dag)


# pylint: disable=redefined-outer-name, protected-access
def test_execution_time_returns_next_execution_time(scheduler, target_execution_time):
    dag = dict(name='BUGUS_DAG', schedule="*/15 * * * *")
    expected_execution_time = target_execution_time.replace(minute=30, second=0, microsecond=0)

    execution_time = scheduler._get_execution_time(target_execution_time, dag)

    assert execution_time == expected_execution_time

# pylint: disable=redefined-outer-name, protected-access
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


# pylint: disable=redefined-outer-name, protected-access
def test_execution_times_are_calculated_correctly(scheduler, schedule, base_time):
    expected_execution_times = [
        datetime(2021, 5, 10, 15, 15, 0),
        datetime(2021, 5, 10, 15, 10, 0),
        datetime(2021, 5, 12, 0, 5, 0)
    ]

    execution_times = scheduler._get_execution_times(schedule, base_time)

    for execution_time,expected_execution_time in zip(execution_times,expected_execution_times):
        assert execution_time.to_pydatetime() == expected_execution_time


# pylint: disable=redefined-outer-name, protected-access
def test_scheduled_dags_are_correctly_identified(scheduler, schedule, base_time):
    schedule["execution_time"] = scheduler._get_execution_times(schedule, base_time)

    scheduled_dags = scheduler._get_scheduled_dags(schedule, base_time)

    assert len(scheduled_dags) == 4
    assert all(actual == expected for actual, expected in zip(scheduled_dags, [True, False, False, True]))


# pylint: disable=redefined-outer-name, protected-access
def test_started_dags_are_correctly_identified(parameters, schedule, base_time):
    scheduler = DAGSchedulerTask(parameters)
    schedule["execution_time"] = scheduler._get_execution_times(schedule, base_time)
    state = DAGState(dict(BASE_PATH=parameters["BASE_PATH"]))

    state.set_dag_status('archive_cat_photos', schedule.execution_time[0].to_pydatetime().isoformat(), Status.PENDING)

    started_dags = scheduler._get_started_dags(schedule)

    assert len(started_dags) == 4
    assert all(actual == expected for actual, expected in zip(started_dags, [True, False, False, False]))


# pylint: disable=redefined-outer-name, protected-access
def test_dags_to_run_are_correctly_identified(parameters, schedule, target_execution_time):
    scheduler = DAGSchedulerTask(parameters)
    execution_times = scheduler._get_execution_times(schedule, target_execution_time - timedelta(minutes=15))
    state = DAGState(dict(BASE_PATH=parameters["BASE_PATH"]))

    dags_to_run = scheduler._determine_dags_to_run(schedule, target_execution_time)

    assert len(dags_to_run) == 2
    assert dags_to_run.name[0] == 'archive_cat_photos'

    state.set_dag_status('archive_cat_photos', execution_times[0].to_pydatetime().isoformat(), Status.PENDING)

    dags_to_run = scheduler._determine_dags_to_run(schedule, target_execution_time)

    assert len(dags_to_run) == 1


# pylint: disable=redefined-outer-name, protected-access
def test_dags_to_run_are_transformed_to_list_of_bytes(parameters, schedule_csv, target_execution_time):
    parameters["data"] = [schedule_csv.encode('utf-8', errors='backslashreplace')]
    scheduler = DAGSchedulerTask(parameters)
    data = None

    with mock.patch('datalabs.etl.dag.schedule.task.DAGSchedulerTask._get_target_execution_time') as get_execution_time:
        get_execution_time.return_value = target_execution_time
        data = scheduler._transform()

    assert len(data) == 1

    dags_to_run = pickle.loads(data[0])

    assert len(dags_to_run) == 2

    dag_data = [json.loads(dag) for dag in dags_to_run]

    for row in dag_data:
        assert all(column in row for column in ['DAG', 'execution_time'])


@pytest.fixture
def state_directory():
    with tempfile.TemporaryDirectory() as directory:
        yield directory


@pytest.fixture
def parameters(state_directory):
    return dict(
        INTERVAL_MINUTES='15',
        DAG_STATE_CLASS='datalabs.etl.dag.state.file.DAGState',
        BASE_PATH=state_directory,
        EXECUTION_TIME='2021-08-02T21:30:00.000000'
    )


@pytest.fixture
def scheduler(parameters):
    return DAGSchedulerTask(parameters)


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
boil_water,*/15 * * * *
"""


@pytest.fixture
def schedule(schedule_csv):
    return pandas.read_csv(BytesIO(schedule_csv.encode('utf8')))
