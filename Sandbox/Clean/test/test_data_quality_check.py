from datetime import datetime
import logging
import tempfile

import mock
import pandas
import pytest

import data_quality_check as dqc

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_failure_count_logger_writes_csv(log_paths):
    LOGGER.debug(log_paths)
    current_date = datetime.utcnow().date().strftime('%Y-%m-%d')
    loggers = dqc.setup_loggers(log_paths)

    loggers.failure_count.info('42')
    LOGGER.debug('Logger Level: %s', loggers.failure_count.level)

    with open(log_paths.failure_count, 'r') as file:
        LOGGER.debug('Contents: %s', file.read())

    data = pandas.read_csv(log_paths.failure_count, names=['date', 'message'])
    LOGGER.debug(data)

    assert data['date'][0] == current_date
    assert data['message'][0] == 42


def test_modification_date(current_date):
    modification_date = None

    with tempfile.TemporaryDirectory() as path:
        modification_date = dqc.modification_date(path)

    assert modification_date == current_date


def test_new_data_available(current_date):
    assert dqc.new_data_available(current_date)


def test_check_disciplinary_action_data_quality(base_path, log_failure_counts):
    log_failure_counts()

    assert log_failure_counts.call_count == 1



@pytest.fixture
def log_paths():
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as failure_count_log_path:
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as file_error_log_path:
            yield dqc.LogPaths(
                failure_count=failure_count_log_path.name,
                file_error=file_error_log_path.name
            )


@pytest.fixture
def current_date():
    return datetime.utcnow().date()


@pytest.fixture
def base_path():
    with tempfile.TemporaryDirectory() as base_path:
        yield base_path


@pytest.fixture
def log_failure_counts():
    with mock.patch('data_quality_check.log_failure_counts') as log_failure_counts:
        yield log_failure_counts
