""" Clear the status of a DAG and it's tasks """
from   enum import Enum
import argparse
import logging

from datalabs.etl.dag.state.dynamodb import DAGState
from datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class DAGClasses(Enum):
    ONEVIEW = "datalabs.etl.dag.oneview.ingest.OneViewDAG"
    CPTAPI = "datalabs.etl.dag.cpt.api.CPTAPIDAG"


def main(args):
    parameters = dict(
        STATE_LOCK_TABLE='N/A',
        DAG_STATE_TABLE=f'DataLake-dag-state-{args["environment"]}',
    )
    state = DAGState(parameters)
    dag_class = import_plugin(DAGClasses.__members__[args["dag"]].value)
    execution_time = f'{args["date"]} {args["time"]}'

    for task in args["task"]:
        if args["upstream"]:
            state.clear_upstream_tasks(dag_class, args["dag"], execution_time, task)
        elif args["downstream"]:
            state.clear_downstream_tasks(dag_class, args["dag"], execution_time, task)
        else:
            state.clear_task(args["dag"], execution_time, task)

if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--dag', required=True, help='DAG ID')
    ap.add_argument('-t', '--task', action='append', required=True, help='task ID')
    ap.add_argument('-D', '--date', required=True, help='YY-MM-DD')
    ap.add_argument('-T', '--time', required=True, help='hh:mm:ss')
    ap.add_argument('-e', '--environment', required=True, help='sbx, dev, tst, itg, or prd')
    ap.add_argument('-p', '--upstream', action='store_true', default=False, help='also clear all upstream tasks')
    ap.add_argument('-w', '--downstream', action='store_true', default=False, help='also clear all downstream tasks')
    args = vars(ap.parse_args())

    try:
        return_code = main(args)
    except Exception as e:
        LOGGER.exception(f'Failed to clear dag task statuses.')
        return_code = 1

    exit(return_code)
