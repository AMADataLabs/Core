""" Clear the status of a DAG and it's tasks """
from   enum import Enum
import argparse
import logging
import re

from datalabs.etl.dag.state.dynamodb import DAGState
from datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class DAGClasses(Enum):
    DAG_SCHEDULER = "datalabs.etl.dag.schedule.dag.DAGSchedulerDAG"
    ECS_SCHEDULER = "datalabs.etl.dag.schedule.dag.DAGSchedulerDAG"
    ONEVIEW = "datalabs.etl.dag.masterfile.oneview.OneViewDAG"
    CPTAPI = "datalabs.etl.dag.cpt.api.CPTAPIDAG"
    HELLO_WORLD_JAVA = "datalabs.example.etl.dag.hello_world_java.HelloWorldJavaDAG"
    LICENSED_ORGANIZATIONS = "datalabs.etl.dag.cpt.organization.LicensedOrganizationDAG"


def main(args):
    parameters = dict(
        STATE_LOCK_TABLE='N/A',
        DAG_STATE_TABLE=f'DataLake-dag-state-{args["environment"]}',
    )
    state = DAGState(parameters)
    dag_class = import_plugin(DAGClasses.__members__[args["dag"]].value)
    execution_time = f'{args["date"]}T{args["time"]}'

    validate_arguments(args)

    if args.get("file") is not None:
        args["task"] = get_tasks_from_file(args["file"])

    for task in args["task"]:
        if args["upstream"]:
            state.clear_upstream_tasks(dag_class, args["dag"], execution_time, task)
        elif args["downstream"]:
            state.clear_downstream_tasks(dag_class, args["dag"], execution_time, task)
        else:
            state.clear_task(args["dag"], execution_time, task)


def validate_arguments(args):
    if args.get("task") is None and args.get("file") is None:
        raise ValueError('One or more task IDs must be specified with either the --task or --file argument.')
    elif args.get("task") is not None and args.get("file") is not None:
        raise ValueError('Only one of the arguments --task or --file is allowed.')

    if re.match('^[1-2][0-9]{3}-[0-1][0-9]-[0-3][0-9]$', args["date"]) is None:
        raise ValueError('The date argument must be in the form YYYY-MM-DD.')

    if re.match('^[0-2][0-9]:[0-5][0-9]:[0-5][0-9]$', args["time"]) is None:
        raise ValueError('The time argument must be in the form HH:MM:SS.')


def get_tasks_from_file(file):
    tasks = []

    with open(file) as file:
        for task in file:
            tasks.append(task.strip())

    return tasks


if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--dag', required=True, help='DAG ID')
    ap.add_argument('-t', '--task', action='append', required=False, help='task ID')
    ap.add_argument('-D', '--date', required=True, help='YY-MM-DD')
    ap.add_argument('-T', '--time', required=True, help='hh:mm:ss')
    ap.add_argument('-e', '--environment', required=True, help='sbx, dev, tst, itg, or prd')
    ap.add_argument('-p', '--upstream', action='store_true', default=False, help='also clear all upstream tasks')
    ap.add_argument('-w', '--downstream', action='store_true', default=False, help='also clear all downstream tasks')
    ap.add_argument('-f', '--file', required=False, help='Task ID list file')
    args = vars(ap.parse_args())

    try:
        return_code = main(args)
    except Exception as e:
        LOGGER.exception('Failed to clear dag task statuses.')
        return_code = 1

    exit(return_code)
