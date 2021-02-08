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


with DAG(
    dag_id='test_pod_xcom',
    default_args={'owner': 'airflow'},
    schedule_interval=None,
    start_date=days_ago(2),
    tags=['testing'],
) as dag:
from pprint import pprint

from airflow import DAG
from kubernetes.client import models as k8s
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago


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
    write_xcom_task = PythonOperator(
        task_id="write_xcom",
        python_callable=write_xcom,
        provide_context=True,
        executor_config={
            "pod_override": k8s.V1Pod(
                spec=k8s.V1PodSpec(
                    containers=[
                        k8s.V1Container(
                            name="base",
                            image="docker-registry.default.svc:5000/hsg-data-labs-dev/airflow-worker:1.0.0"
                        )
                    ]
                )
            ),
        },
    )


    # write_xcom = KubernetesPodOperator(
    #     namespace='hsg-data-labs-dev',
    #     cmds=["sh", "-c", "mkdir -p /airflow/xcom/;echo '[1,2,3,4]' > /airflow/xcom/return.json"],
    #     name="write-xcom",
    #     do_xcom_push=True,
    #     is_delete_operator_pod=True,
    #     in_cluster=True,
    #     task_id="write-xcom",
    #     get_logs=True,
    #     executor_config={
    #         "pod_override": k8s.V1Pod(
    #             spec=k8s.V1PodSpec(
    #                 containers=[
    #                     k8s.V1Container(
    #                         name="base",
    #                         image="docker-registry.default.svc:5000/hsg-data-labs-dev/airflow-worker:1.0.0"
    #                     )
    #                 ]
    #             )
    #         ),
    #     },
    # )


    read_xcom_task = PythonOperator(
        task_id="read_xcom",
        python_callable=read_xcom,
        provide_context=True,
        executor_config={
            "pod_override": k8s.V1Pod(
                spec=k8s.V1PodSpec(
                    containers=[
                        k8s.V1Container(
                            name="base",
                            image="docker-registry.default.svc:5000/hsg-data-labs-dev/airflow-worker:1.0.0"
                        )
                    ]
                )
            ),
        },
    )
    #
    # pod_task_xcom_result = BashOperator(
    #     bash_command="echo \"{{ task_instance.xcom_pull('write-xcom')[0] }}\"",
    #     task_id="pod_task_xcom_result",
    # )


write_xcom_task >> read_xcom_task
