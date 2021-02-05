from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.utils.dates import days_ago

with DAG(
    dag_id='test_pod_xcom',
    default_args={'owner': 'airflow'},
    schedule_interval=None,
    start_date=days_ago(2),
    tags=['example'],
) as dag:
    write_xcom = KubernetesPodOperator(
        namespace='hsg-data-labs',
        pod_template_file='/home/airflow/worker.yaml',
        image='alpine',
        cmds=["sh", "-c", "mkdir -p /airflow/xcom/;echo '[1,2,3,4]' > /airflow/xcom/return.json"],
        name="write-xcom",
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="write-xcom",
        get_logs=True
    )

    pod_task_xcom_result = BashOperator(
        bash_command="echo \"{{ task_instance.xcom_pull('write-xcom')[0] }}\"",
        task_id="pod_task_xcom_result",
    )

write_xcom >> pod_task_xcom_result
