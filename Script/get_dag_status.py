""" Clear the status of a DAG and it's tasks """
import argparse
import logging

from datalabs.etl.dag.state import Status
from datalabs.etl.dag.state.dynamodb import DAGState

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def main(args):
    parameters = dict(
        STATE_LOCK_TABLE='N/A',
        DAG_STATE_TABLE=f'DataLake-dag-state-{args["environment"]}'
    )
    state = DAGState(parameters)
    execution_time = f'{args["date"]}T{args["time"]}'

    if not args["task"]:
        statuses = state.get_all_statuses(args["dag"], execution_time)
    else:
        statuses = state.get_task_statuses(args["dag"], execution_time, args["task"])

    if statuses:
        print(f'DAG: {statuses.get(args["dag"], Status.UNKNOWN).value}')
        if args["dag"] in statuses:
            statuses.pop(args["dag"])

        for task in sorted(statuses.keys()):
            if not args["not_finished"] or statuses[task] != Status.FINISHED:
                print(f'{task}: {statuses[task].value}')
    else:
        print(f'No status was found for {args["dag"]} run {args["date"]} {args["time"]}.')

if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--dag', required=True, help='DAG name')
    ap.add_argument('-t', '--task', action='append', required=False, help='task ID')
    ap.add_argument('-D', '--date', required=True, help='YY-MM-DD')
    ap.add_argument('-T', '--time', required=True, help='hh:mm:ss')
    ap.add_argument('-e', '--environment', required=True, help='sbx, dev, tst, itg, prd, or local')
    ap.add_argument('-F', '--not-finished', action='store_true', help='Filter out Finished tasks')
    args = vars(ap.parse_args())

    try:
        return_code = main(args)
    except Exception as e:
        LOGGER.exception(f'Failed to get dag task statuses.')
        return_code = 1

    exit(return_code)
