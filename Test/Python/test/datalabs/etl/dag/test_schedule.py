""" Source: datalabs.etl.dag.schedule """
from   datetime import datetime
from   io import BytesIO
import logging
import tempfile

import mock
import pandas
import pytest

from   datalabs.etl.dag.schedule import DAGScheduler, DAGSchedulerParameters

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_getting_state_plugin(parameters):
    scheduler = DAGScheduler(parameters)
    state = scheduler._get_state_plugin()

    assert hasattr(state, 'get_status')
    assert state.get_status('BOGUS_DAG', datetime.now()).name == 'Unknown'


def test_dag_flagged_not_started_if_no_state(parameters):
    scheduler = DAGScheduler(parameters)
    state = scheduler._get_state_plugin()
    dag = dict(name='BUGUS_DAG', execution_time=datetime.now())

    started = scheduler._is_started(state, dag)

    assert started == False


def test_execution_time_returns_next_execution_time(parameters, base_time):
    scheduler = DAGScheduler(parameters)
    dag = dict(name='BUGUS_DAG', schedule="*/15 * * * *")
    expected_execution_time = base_time.replace(minute=30, second=0, microsecond=0)

    execution_time = scheduler._get_execution_time(base_time, dag)

    assert execution_time == expected_execution_time

def test_execution_time_bounds_are_correct(parameters, base_time):
    scheduler = DAGScheduler(parameters)

    lower_bound, upper_bound = scheduler._get_execution_time_bounds(base_time)

    assert lower_bound.year == base_time.year
    assert lower_bound.month == base_time.month
    assert lower_bound.day == base_time.day
    assert lower_bound.hour == base_time.hour
    assert lower_bound.minute == 30
    assert lower_bound.second == 0
    assert lower_bound.microsecond == 0

    assert upper_bound.year == base_time.year
    assert upper_bound.month == base_time.month
    assert upper_bound.day == base_time.day
    assert upper_bound.hour == base_time.hour
    assert upper_bound.minute == 45
    assert upper_bound.second == 0
    assert upper_bound.microsecond == 0


def test_execution_times_are_calculated_correctly(parameters, schedule_csv):
    scheduler = DAGScheduler(parameters)
    schedule = pandas.read_csv(BytesIO(schedule_csv.encode('utf8')))

    execution_times = self._get_execution_times(schedule, now)

    assert


def test_started_dags_are_correctly_identified(parameters, schedule_csv):
    scheduler = DAGScheduler(parameters)
    schedule = pandas.read_csv(BytesIO(schedule_csv.encode('utf8')))
    schedule["execution_time"] = self._get_execution_times(schedule, now)

    started_dags = scheduler._get_started_dags(schedule)

    assert len(started_dags) == 3
    assert started_dags[0] == True
    assert started_dags[1] == True
    assert started_dags[2] == False

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
def base_time():
    return datetime(2021, 5, 10, 15, 20, 25)


@pytest.fixture
def schedule_csv():
    return """name,schedule
archive_cat_photos,5 * */1 * 1
translate_meows,10 */5 * * 1-5
scrape_ama_fan_pages,5 * */1 * 3
"""
