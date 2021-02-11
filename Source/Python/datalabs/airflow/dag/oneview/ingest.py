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

    type_of_practice_extractor = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, aims],
        env=dict(TASK_CLASS=datalabs.etl.jdbc.extract.JDBCExtractorTask),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="type_of_practice_extractor",
        get_logs=True,
    )

    type_of_practice_transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env=dict(TASK_WRAPPER_CLASS=datalabs.etl.kubernetes.ETLComponentTaskWrapper),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="type_of_practice_transformer",
        get_logs=True,
    )

    type_of_practice_loader = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, minio],
        env=dict(TASK_WRAPPER_CLASS=datalabs.etl.kubernetes.ETLComponentTaskWrapper),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="type_of_practice_loader",
        get_logs=True,
    )

    specialty_merge_extractor = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, aims],
        env=dict(TASK_CLASS=datalabs.etl.jdbc.extract.JDBCExtractorTask),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="specialty_merge_extractor",
        get_logs=True,
    )

    specialty_merge_transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env=dict(TASK_WRAPPER_CLASS=datalabs.etl.kubernetes.ETLComponentTaskWrapper),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="specialty_merge_transformer",
        get_logs=True,
    )

    specialty_merge_loader = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, minio],
        env=dict(TASK_WRAPPER_CLASS=datalabs.etl.kubernetes.ETLComponentTaskWrapper),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="specialty_merge_loader",
        get_logs=True,
    )

    specialty_extractor = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, aims],
        env=dict(TASK_CLASS=datalabs.etl.jdbc.extract.JDBCExtractorTask),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="specialty_extractor",
        get_logs=True,
    )

    specialty_transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env=dict(TASK_WRAPPER_CLASS=datalabs.etl.kubernetes.ETLComponentTaskWrapper),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="specialty_transformer",
        get_logs=True,
    )

    specialty_loader = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, minio],
        env=dict(TASK_WRAPPER_CLASS=datalabs.etl.kubernetes.ETLComponentTaskWrapper),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="specialty_loader",
        get_logs=True,
    )

type_of_practice_extractor >> type_of_practice_transformer >> type_of_practice_loader
specialty_merge_extractor >> specialty_merge_transformer >> specialty_merge_loader
specialty_extractor >> specialty_transformer >> specialty_loader
