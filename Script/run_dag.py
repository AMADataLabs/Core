""" Clear the status of a DAG and it's tasks """
import argparse
import json
import logging

from   datalabs.access.aws import AWSClient
from   datalabs.etl.dag.celery.task import run_dag_processor

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


ACCOUNTS = dict(
    sbx="644454719059",
    dev="191296302136",
    tst="194221139997",
    stg="340826698851",
    itg="285887636563",
    prd="285887636563"
)


def main(args):
    if args["environment"] == 'local':
        run_local_dag(args)
    else:
        run_remote_dag(args) 
    
    
def run_local_dag(args):
    run_dag_processor(args["dag"], args["time"], args["parameters"])

def run_remote_dag(args):

    topic_arn = f'arn:aws:sns:us-east-1:{ACCOUNTS[args["environment"]]}:DataLake-{args["environment"]}-DAGProcessor'
    message = dict(
        dag=args["dag"],
        execution_time=f'{args["date"]} {args["time"]}'
    )

    if args["parameters"]:
        message["parameters"] = dict(args["parameters"])

    with AWSClient('sns') as sns:
        sns.publish(
            TargetArn=topic_arn,
            Message=json.dumps(message)
        )

if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--dag', required=True, help='DAG name')
    ap.add_argument('-e', '--environment', required=True, help='sbx, dev, tst, itg, prd, or local')
    ap.add_argument('-D', '--date', required=True, help='Execution date of the form YYYY-MM-DD')
    ap.add_argument('-T', '--time', required=True, help='Execution time of the form HH:MM:SS')
    ap.add_argument('-p', '--parameters', action='append', required=False, help='Dynamic global DAG plugin variables')
    args = vars(ap.parse_args())

    try:
        return_code = main(args)
    except Exception as e:
        LOGGER.exception(f'Failed to clear dag task statuses.')
        return_code = 1

    exit(return_code)
