""" Clear the status of a DAG and it's tasks """
import argparse
import logging

from datalabs.etl.dag.state.dynamodb import DAGState

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def main(args):
    parameters = dict(
        LOCK_TABLE='N/A',
        STATE_TABLE=f'DataLake-dag-state-{args["environment"]}',
    )
    state = DAGState(parameters)
    limit = None

    if args["limit"]:
        limit = int(args["limit"])

    run_info = state.get_dag_runs(args["dag"], limit=limit)

    for iso_execution_time, status in run_info.items():
        execution_time = iso_execution_time.replace("T", " ")
        if execution_time == iso_execution_time:
          execution_time = "*" + execution_time

        print(f'{execution_time} {status}')

if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--dag', required=True, help='DAG name')
    ap.add_argument('-n', '--limit', default=None, help='maximum number of results (default=10)')
    ap.add_argument('-e', '--environment', required=True, help='sbx, dev, tst, itg, or prd')
    args = vars(ap.parse_args())

    try:
        return_code = main(args)
    except Exception as e:
        LOGGER.exception(f'Failed to get DAG runs.')
        return_code = 1

    exit(return_code)
