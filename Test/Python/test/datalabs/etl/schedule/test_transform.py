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
def test_scheduled_identifier_dags_to_run_are_correctly_identified(parameters_identify_scheduled_dag, schedule_one_dag_run_per_day, \
        target_execution_time_identify_scheduled_dag):
    scheduler = ScheduledDAGIdentifierTask(parameters_identify_scheduled_dag)

    dags_to_run = scheduler._determine_dags_to_run(schedule_one_dag_run_per_day, \
            target_execution_time_identify_scheduled_dag).reset_index()

    start_at =  target_execution_time_identify_scheduled_dag - timedelta(days=1)
    stop_at =  target_execution_time_identify_scheduled_dag

    assert start_at == datetime(2023, 8, 30, 13, 0)
    assert stop_at == datetime(2023, 8, 31, 13, 0)

    assert len(dags_to_run) == 2
    assert dags_to_run.dag[0] == 'ADDRESS_LOAD_COMPILER'
    assert dags_to_run.execution_time[0] == datetime(2023, 8, 30, 13, 0)

    assert dags_to_run.dag[1] == 'LICENSE_MOVEMENT'
    assert dags_to_run.execution_time[1] == datetime(2023, 8, 30, 13, 5)

# pylint: disable=redefined-outer-name, protected-access, line-too-long
def test_repeatly_scheduled_identifier_dags_to_run_are_correctly_identified(parameters_identify_scheduled_dag, schedule_one_dag_run_repeatly, \
        target_execution_time_identify_scheduled_dag):
    scheduler = ScheduledDAGIdentifierTask(parameters_identify_scheduled_dag)

    dags_to_run = scheduler._determine_dags_to_run(schedule_one_dag_run_repeatly, \
            target_execution_time_identify_scheduled_dag).reset_index()

    start_at =  target_execution_time_identify_scheduled_dag - timedelta(days=1)
    stop_at =  target_execution_time_identify_scheduled_dag

    assert start_at == datetime(2023, 8, 30, 13, 0)
    assert stop_at == datetime(2023, 8, 31, 13, 0)

    assert len(dags_to_run) == 110

    assert dags_to_run.dag[0] == 'LICENSE_MOVEMENT'
    assert dags_to_run.execution_time[0] == datetime(2023, 8, 30, 13, 5)

    assert dags_to_run.dag[1] == 'CERNER_REPORT'
    assert dags_to_run.execution_time[1] == datetime(2023, 8, 30, 13, 0)
    assert dags_to_run.execution_time[2] == datetime(2023, 8, 30, 13, 15)
    assert dags_to_run.execution_time[96] == datetime(2023, 8, 31, 12, 45)

    assert dags_to_run.dag[97] == 'VERICRE_DATA_STEWARD'
    assert dags_to_run.execution_time[97] == datetime(2023, 8, 31, 0, 0)
    assert dags_to_run.execution_time[98] == datetime(2023, 8, 31, 1, 0)
    assert dags_to_run.execution_time[109] == datetime(2023, 8, 31, 12, 0)


# pylint: disable=redefined-outer-name, protected-access, line-too-long
def test_scheduled_dags_to_run_are_correctly_identified_edge_cases(parameters_identify_scheduled_dag_test, schedule_one_dag_run_repeatly, \
        target_execution_time_identify_scheduled_dag_test):
    scheduler = ScheduledDAGIdentifierTask(parameters_identify_scheduled_dag_test)

    dags_to_run = scheduler._determine_dags_to_run(schedule_one_dag_run_repeatly, \
            target_execution_time_identify_scheduled_dag_test)

    start_at =  target_execution_time_identify_scheduled_dag_test - timedelta(days=1)
    stop_at =  target_execution_time_identify_scheduled_dag_test

    assert start_at == datetime(2023, 8, 30, 13, 20)
    assert stop_at == datetime(2023, 8, 31, 13, 20)

    assert len(dags_to_run) == 110
    assert dags_to_run.dag[0] == 'CERNER_REPORT'
    assert dags_to_run.execution_time[0] == datetime(2023, 8, 30, 13, 30)
    assert dags_to_run.execution_time[95] == datetime(2023, 8, 31, 13, 15)


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
def parameters_identify_scheduled_dag(state_directory):
    return dict(
        INTERVAL_MINUTES='15',
        DAG_STATE=json.dumps(
            dict(
                CLASS='datalabs.etl.dag.state.file.DAGState',
                BASE_PATH=state_directory
            )
        ),
        EXECUTION_TIME='2023-08-31T13:00:00.000000'
    )


@pytest.fixture
def parameters_identify_scheduled_dag_test(state_directory):
    return dict(
        INTERVAL_MINUTES='15',
        DAG_STATE=json.dumps(
            dict(
                CLASS='datalabs.etl.dag.state.file.DAGState',
                BASE_PATH=state_directory
            )
        ),
        EXECUTION_TIME='2023-08-31T13:20:00.000000'
    )


@pytest.fixture
def target_execution_time_identify_scheduled_dag():
    return datetime(2023, 8, 31, 13, 0, 0)


@pytest.fixture
def target_execution_time_identify_scheduled_dag_test():
    return datetime(2023, 8, 31, 13, 20, 0)


@pytest.fixture
def schedule_one_dag_run_per_day_csv():
    return """dag,schedule
ADDRESS_LOAD_COMPILER,0 13 * * mon-fri
DBL,13 0 * * tue-sat
DEVELOPER_EMAILS,0 0 * * sun-thu
LICENSE_MOVEMENT,5 13 * * mon-fri
"""


@pytest.fixture
def schedule_one_dag_run_per_day(schedule_one_dag_run_per_day_csv):
    return pandas.read_csv(BytesIO(schedule_one_dag_run_per_day_csv.encode('utf8')))


@pytest.fixture
def schedule_one_dag_run_repeatly_csv():
    return """dag,schedule
CERNER_REPORT,*/15 * * * *
PLATFORM_USER_TOKENS,13 0 * * tue-sat
VERICRE_DATA_STEWARD,0 */1 * * thu-fri
LICENSE_MOVEMENT,5 13 * * mon-fri
"""

@pytest.fixture
def schedule_one_dag_run_repeatly(schedule_one_dag_run_repeatly_csv):
    return pandas.read_csv(BytesIO(schedule_one_dag_run_repeatly_csv.encode('utf8')))
