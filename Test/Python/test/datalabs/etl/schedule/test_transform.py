""" Source: datalabs.etl.schedule.task """
from   datetime import datetime, timedelta
from   io import BytesIO
import json
import logging
import tempfile

import mock
import pandas
import pytest

from   datalabs.etl.schedule.transform import DAGSchedulerTask, ScheduledDAGIdentifierTask
from   datalabs.etl.dag.state.base import Status
from   datalabs.etl.dag.state.file import DAGState

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_getting_state_plugin(scheduler, parameters):
    state = scheduler._get_state_plugin(parameters)

    assert state.get_dag_status('BOGUS_DAG', datetime.utcnow().isoformat()) == Status.UNKNOWN


# pylint: disable=redefined-outer-name, protected-access
def test_dag_flagged_not_started_if_no_state(scheduler, parameters):
    state = scheduler._get_state_plugin(parameters)
    dag = dict(dag='BUGUS_DAG', execution_time=pandas.Timestamp(datetime.utcnow()))

    assert not scheduler._is_started(state, dag)


# pylint: disable=redefined-outer-name, protected-access
def test_execution_time_returns_next_execution_time(scheduler, target_execution_time):
    dag = dict(dag='BUGUS_DAG', schedule="*/15 * * * *")
    expected_execution_time = target_execution_time.replace(minute=30, second=0, microsecond=0)

    execution_time = scheduler._get_execution_time(target_execution_time, dag)

    assert execution_time == expected_execution_time


# pylint: disable=redefined-outer-name, protected-access
def test_execution_time_bounds_are_correct(scheduler, target_execution_time):
    lower_bound, upper_bound = scheduler._get_execution_time_bounds(target_execution_time)

    _assert_lower_execution_time_bounds_are_correct(lower_bound, target_execution_time)

    _assert_upper_execution_time_bounds_are_correct(upper_bound, target_execution_time)


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
    state = DAGState(dict(BASE_PATH=json.loads(parameters["DAG_STATE"])["BASE_PATH"]))

    state.set_dag_status('archive_cat_photos', schedule.execution_time[0].to_pydatetime().isoformat(), Status.PENDING)

    started_dags = scheduler._get_started_dags(schedule)

    assert len(started_dags) == 4
    assert all(actual == expected for actual, expected in zip(started_dags, [True, False, False, False]))


# pylint: disable=redefined-outer-name, protected-access
def test_dags_to_run_are_correctly_identified(parameters, schedule, target_execution_time):
    scheduler = DAGSchedulerTask(parameters)
    execution_times = scheduler._get_execution_times(schedule, target_execution_time - timedelta(minutes=int('15')))
    state = DAGState(dict(BASE_PATH=json.loads(parameters["DAG_STATE"])["BASE_PATH"]))

    dags_to_run = scheduler._determine_dags_to_run(schedule, target_execution_time)

    assert len(dags_to_run) == 2
    assert dags_to_run.dag[0] == 'archive_cat_photos'

    state.set_dag_status('archive_cat_photos', execution_times[0].to_pydatetime().isoformat(), Status.PENDING)

    dags_to_run = scheduler._determine_dags_to_run(schedule, target_execution_time)

    assert len(dags_to_run) == 1


# pylint: disable=redefined-outer-name, protected-access
def test_dags_to_run_handles_empty_schedule_nicely(parameters, empty_schedule, target_execution_time):
    scheduler = DAGSchedulerTask(parameters)

    dags_to_run = scheduler._determine_dags_to_run(empty_schedule, target_execution_time)

    assert len(dags_to_run) == 0


# pylint: disable=redefined-outer-name, protected-access
def test_dags_to_run_are_transformed_to_list_of_bytes(parameters, schedule_csv, target_execution_time):
    data = [schedule_csv.encode('utf-8', errors='backslashreplace')]
    scheduler = DAGSchedulerTask(parameters, data)
    data = None

    with mock.patch('datalabs.etl.schedule.transform.DAGSchedulerTask._get_target_execution_time') \
            as get_execution_time:
        get_execution_time.return_value = target_execution_time
        data = scheduler.run()

    assert len(data) == 1

    dags_to_run = json.loads(data[0].decode())

    assert len(dags_to_run) == 2

    for row in dags_to_run:
        assert all(column in row for column in ['dag', 'execution_time'])

# pylint: disable=redefined-outer-name, protected-access, line-too-long
def test_previous_days_dag_runs_are_correctly_identified(
        parameters_get_last_days_runs,
        schedule_get_last_days_runs,
        target_execution_time_get_last_days_runs
):
    scheduler = ScheduledDAGIdentifierTask(parameters_get_last_days_runs)

    dags_to_run = scheduler._determine_dags_to_run(
            schedule_get_last_days_runs,
            target_execution_time_get_last_days_runs
    ).reset_index()

    assert len(dags_to_run) == 112

    assert dags_to_run.DAG[0] == 'CERNER_REPORT'
    assert dags_to_run.Run[0] == datetime(2023, 8, 30, 13, 30)
    assert dags_to_run.Run[95] == datetime(2023, 8, 31, 13, 15)

    assert dags_to_run.DAG[96] == 'PLATFORM_USER_TOKENS'
    assert dags_to_run.Run[96] == datetime(2023, 8, 31, 0, 13)

    assert dags_to_run.DAG[97] == 'LICENSE_MOVEMENT'
    assert dags_to_run.Run[97] == datetime(2023, 8, 31, 13, 5)

    assert dags_to_run.DAG[98] == 'VERICRE_DATA_STEWARD'
    assert dags_to_run.Run[98] == datetime(2023, 8, 31, 0, 0)
    assert dags_to_run.Run[99] == datetime(2023, 8, 31, 1, 0)
    assert dags_to_run.Run[111] == datetime(2023, 8, 31, 13, 0)


def _assert_lower_execution_time_bounds_are_correct(lower_bound, target_execution_time):
    assert lower_bound.year == target_execution_time.year
    assert lower_bound.month == target_execution_time.month
    assert lower_bound.day == target_execution_time.day
    assert lower_bound.hour == target_execution_time.hour
    assert lower_bound.minute == 30
    assert lower_bound.second == 0
    assert lower_bound.microsecond == 0


def _assert_upper_execution_time_bounds_are_correct(upper_bound, target_execution_time):
    assert upper_bound.year == target_execution_time.year
    assert upper_bound.month == target_execution_time.month
    assert upper_bound.day == target_execution_time.day
    assert upper_bound.hour == target_execution_time.hour
    assert upper_bound.minute == 45
    assert upper_bound.second == 0
    assert upper_bound.microsecond == 0


@pytest.fixture
def state_directory():
    with tempfile.TemporaryDirectory() as directory:
        yield directory


@pytest.fixture
def parameters(state_directory):
    return dict(
        INTERVAL_MINUTES='15',
        DAG_STATE=json.dumps(
            dict(
                CLASS='datalabs.etl.dag.state.file.DAGState',
                BASE_PATH=state_directory
            )
        ),
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
    return """dag,schedule
archive_cat_photos,15 * */1 * 1
translate_meows,10 */5 * * 1-5
scrape_ama_fan_pages,"5 * */1 * 3,4"
boil_water,*/15 * * * *
"""


@pytest.fixture
def empty_schedule_csv():
    return """name,schedule
"""


@pytest.fixture
def schedule(schedule_csv):
    return pandas.read_csv(BytesIO(schedule_csv.encode('utf8')))


@pytest.fixture
def empty_schedule(empty_schedule_csv):
    return pandas.read_csv(BytesIO(empty_schedule_csv.encode('utf8')))


@pytest.fixture
def parameters_get_last_days_runs(state_directory):
    return dict(
        DAG_STATE=json.dumps(
            dict(
                CLASS='datalabs.etl.dag.state.file.DAGState',
                BASE_PATH=state_directory
            )
        ),
        EXECUTION_TIME='2023-08-31T13:20:00.000000'
    )


@pytest.fixture
def target_execution_time_get_last_days_runs():
    return datetime(2023, 8, 31, 13, 20, 0)


@pytest.fixture
def schedule_get_last_days_runs_csv():
    """ Given an execution_time of 2023-08-31 13:20:00, we would expect the following DAG runs:
            CERNER_REPORT 2023-08-30 13:30:00
            . . .
            CERNER_REPORT 2023-08-31 13:15:00
            PLATFORM_USER_TOKENS 2023-08-31 00:13:00
            LICENSE_MOVEMENT 2023-08-31 13:05:00
            VERICRE_DATA_STEWARD 2023-08-31 00:00:00
            . . .
            VERICRE_DATA_STEWARD 2023-08-31 13:00:00
    """
    return """dag,schedule
CERNER_REPORT,*/15 * * * *
PLATFORM_USER_TOKENS,13 0 * * tue-sat
LICENSE_MOVEMENT,5 13 * * mon-fri
VERICRE_DATA_STEWARD,0 * * * thu-fri
"""

@pytest.fixture
def schedule_get_last_days_runs(schedule_get_last_days_runs_csv):
    return pandas.read_csv(BytesIO(schedule_get_last_days_runs_csv.encode('utf8')))
