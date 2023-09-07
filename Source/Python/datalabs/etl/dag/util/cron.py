""" Utility functions for processing DAG crontab data. """
from   datetime import datetime, timedelta
from   itertools import takewhile

from   croniter import croniter
import pandas


# pylint: disable=unsupported-assignment-operation, no-member
def get_last_days_runs(file, now=None):
    schedule = pandas.read_csv(file)
    now = datetime.utcnow() if now is None else now
    base_time = now - timedelta(hours=24)

    dag_runs = schedule.schedule.apply(lambda cron_descriptor: croniter(cron_descriptor, base_time))

    schedule["run"] = dag_runs.apply(lambda x: list(takewhile(lambda y: y <= now, get_dag_runs(x))))

    schedule.drop(columns="schedule", inplace=True)

    return schedule.explode("run")


def get_dag_runs(dag_runs):
    """ Generator wrapper around croniter.get_next(return_type)
        since it doesn't follow the standard iterator interface.
    """
    yield dag_runs.get_next(datetime)
