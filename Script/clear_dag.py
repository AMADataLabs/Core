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
    execution_time = f'{args["date"]}T{args["time"]}'

    state.clear_all(args["dag"], execution_time)

if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--dag', required=True, help='DAG name')
    ap.add_argument('-D', '--date', required=True, help='YY-MM-DD')
    ap.add_argument('-T', '--time', required=True, help='hh:mm:ss')
    ap.add_argument('-e', '--environment', required=True, help='sbx, dev, tst, itg, or prd')
    args = vars(ap.parse_args())

    try:
        return_code = main(args)
    except Exception as e:
        LOGGER.exception(f'Failed to clear dag task statuses.')
        return_code = 1

    exit(return_code)
