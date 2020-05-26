from datetime import datetime
import logging
import tempfile

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


@pytest.fixture
def log_paths():
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as failure_count_log_path:
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as file_error_log_path:
            yield dqc.LogPaths(
                failure_count=failure_count_log_path.name,
                file_error=file_error_log_path.name
            )
