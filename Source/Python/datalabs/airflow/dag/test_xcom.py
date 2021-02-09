import logging

from airflow import DAG
from kubernetes.client import models as k8s
from airflow.operators.bash import BashOperator
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def write_xcom(datestamp, **kwargs):
    task_id = kwargs['task'].task_id
    pprint(kwargs)
    print(datestamp)

    return [1, 2, 3, 4]


def read_xcom(datestamp, **kwargs):
    task_id = kwargs['task'].task_id
    pprint(kwargs)
    print(datestamp)
    print(kwargs['task_instance'].xcom_pull(task_ids='write_xcom'))


with DAG(
    dag_id='test_xcom',
    default_args={'owner': 'airflow'},
    schedule_interval=None,
    start_date=days_ago(2),
    tags=['testing'],
) as dag:
    write_xcom_task = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image="docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0",
        cmds=["sh", "-c", "mkdir -p /airflow/xcom/;echo '[1,2,3,4]' > /airflow/xcom/return.json"],
        name="write-xcom",
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="write-xcom",
        get_logs=True,
        # executor_config={
        #     "pod_override": k8s.V1Pod(
        #         spec=k8s.V1PodSpec(
        #             containers=[
        #                 k8s.V1Container(
        #                     name="base",
        #                     image="docker-registry.default.svc:5000/hsg-data-labs-dev/airflow-worker:1.0.2"
        #                 )
        #             ]
        #         )
        #     ),
        # },
    )


    read_xcom_task = BashOperator(
        bash_command="echo \"{{ task_instance.xcom_pull('write-xcom')[0] }}\"",
        task_id="pod_task_xcom_result",
    )


write_xcom_task >> read_xcom_task
