from pprint import pprint

from airflow import DAG
from kubernetes.client import models as k8s
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago


def print_that(**kwargs):
    pprint(kwargs)
    print(kwargs['ds'])

    return "Foobiddy Doobiddy"


def on_failure_callback(context):
    dag_run = context.get('dag_run')
    task_instances = dag_run.get_task_instances()
    print(f'Failure: {task_instances}')


def on_success_callback(context):
    dag_run = context.get('dag_run')
    task_instances = dag_run.get_task_instances()
    print(f'Success: {task_instances}')


with DAG(
    dag_id='test_python',
    default_args={'owner': 'airflow'},
    schedule_interval=None,
    start_date=days_ago(2),
    tags=['testing'],
    on_failure_callback=on_failure_callback,
    on_success_callback=on_success_callback,
) as dag:
    do_it = PythonOperator(
        task_id="do-it",
        python_callable=print_that,
    )


    do_it_again = PythonOperator(
        task_id="do-it-again",
        python_callable=print_that,
    )


do_it >> do_it_again
