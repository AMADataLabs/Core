from airflow import DAG
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s

etl_config = [
    k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name='oneview-type-of-practice'))
]
minio = [
    k8s.V1EnvFromSource(secret_ref=k8s.V1ConfigMapEnvSource(name='minio-secret'))
]
aims = [
    k8s.V1EnvFromSource(secret_ref=k8s.V1ConfigMapEnvSource(name='aims-secret'))
]

with DAG(
        dag_id='type_of_practice',
        default_args={'owner': 'airflow'},
        schedule_interval=None,
        start_date=days_ago(2),
        tags=['OneView'],
) as dag:

    extractor = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        cmds=['python', 'task.py'],
        env_from=[etl_config, aims],
        env=dict(TASK_CLASS=datalabs.etl.jdbc.extract.JDBCExtractorTask),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="write-xcom",
        get_logs=True,
    )

    transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        cmds=['python', 'task.py'],
        env_from=etl_config,
        env=dict(TASK_CLASS=datalabs.etl.oneview.reference.transform.TypeOfPracticeTransformerTask),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="write-xcom",
        get_logs=True,
    )

    loader = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        cmds=['python', 'task.py'],
        env_from=[etl_config, minio],
        env=dict(TASK_CLASS=datalabs.etl.s3.load.S3UnicodeTextFileLoaderTask),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="write-xcom",
        get_logs=True,
    )

extractor >> loader >> transformer
