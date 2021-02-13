''' Example DAG to test XCOM and the KubernetesPodOperator'''
import logging
from   pprint import pprint

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def write_xcom(datestamp, **kwargs):
    task_id = kwargs['task'].task_id
    pprint(kwargs)
    print(datestamp)
    print(task_id)

    return [1, 2, 3, 4]


def read_xcom(datestamp, **kwargs):
    task_id = kwargs['task'].task_id
    pprint(kwargs)
    print(datestamp)
    print(task_id)
    print(kwargs['task_instance'].xcom_pull(task_ids='write_xcom'))


TEST_XCOM_DAG = DAG(
    dag_id='test_xcom',
    default_args={'owner': 'airflow'},
    schedule_interval=None,
    start_date=days_ago(2),
    tags=['testing'],
)


with TEST_XCOM_DAG:
    WRITE_XCOM_TASK = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image="docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0",
        cmds=["sh", "-c", "mkdir -p /airflow/xcom/;echo '[1,2,3,4]' > /airflow/xcom/return.json"],
        name="write-xcom",
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="write-xcom",
        get_logs=True,
    )


    READ_XCOM_TASK = BashOperator(
        bash_command="echo \"{{ task_instance.xcom_pull('write-xcom')[0] }}\"",
        task_id="pod_task_xcom_result",
    )


# pylint: disable=pointless-statement
WRITE_XCOM_TASK >> READ_XCOM_TASK
