from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s

extractor_config = [
    k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name='oneview-type-of-practice')),
]

with DAG(
        dag_id='type_of_practice',
        default_args={'owner': 'airflow'},
        schedule_interval=None,
        start_date=days_ago(2),
        tags=['TypeOfPractice'],
) as dag:

    extractor = KubernetesPodOperator(
        namespace='default',
        image='alpine',
        cmds=['python', 'task.py'],
        env_from=extractor_config,
        env=dict(TASK_CLASS=datalabs.etl.jdbc.extract.JDBCExtractorTask),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="write-xcom",
        get_logs=True,
    )

    transformer = KubernetesPodOperator(
        namespace='default',
        image='alpine',
        cmds=['python', 'task.py'],
        env_from=extractor_config,
        env=dict(TASK_CLASS=datalabs.etl.s3.load.S3UnicodeTextFileLoaderTask),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="write-xcom",
        get_logs=True,
    )

    loader = KubernetesPodOperator(
        namespace='default',
        image='alpine',
        cmds=['python', 'task.py'],
        env_from=extractor_config,
        env=dict(TASK_CLASS=datalabs.etl.s3.load.S3UnicodeTextFileLoaderTask),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="write-xcom",
        get_logs=True,
    )

    pod_task_xcom_result = BashOperator(
        bash_command="echo \"{{ task_instance.xcom_pull('write-xcom')[0] }}\"",
        task_id="pod_task_xcom_result",
    )

extractor >> loader >> transformer
