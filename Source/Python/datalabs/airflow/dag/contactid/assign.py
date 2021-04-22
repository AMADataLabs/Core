''' Masterfile OneView DAG definition. '''
from airflow import DAG
from airflow.kubernetes.secret import Secret
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s


# ETL_CONFIG = k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name='oneview-etl'))
# MINIO_SECRET = Secret('env', None, 'oneview-etl-minio')
# AIMS_SECRET = Secret('env', None, 'oneview-etl-aims')
# ODS_SECRET = Secret('env', None, 'oneview-etl-ods')
# SFTP_SECRET = Secret('env', None, 'oneview-etl-sftp')
# DATABASE_SECRET = Secret('env', None, 'oneview-etl-database')
DOCKER_IMAGE = 'docker-registry.default.svc:5000/hsg-data-labs-dev/contact-id-etl:0.0.1'

CONTACT_ID_ASSIGNMENT_DAG = DAG(
    dag_id='contact_id',
    default_args={'owner': 'airflow'},
    schedule_interval=None,
    start_date=days_ago(2),
    tags=['ContactID'],
)


with CONTACT_ID_ASSIGNMENT_DAG:
    EXTRACT_ADVANTAGE = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="extract_present_employment",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        # env_from=[ETL_CONFIG],
        # secrets=[ODS_SECRET, MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="extract_advantage",
        get_logs=True,
    )

    EXTRACT_ORG_MANAGER = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="extract_type_of_practice",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        # env_from=[ETL_CONFIG],
        # secrets=[ODS_SECRET, MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="extract_org_manager",
        get_logs=True,
    )

    EXTRACT_VALID = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="extract_ppd",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        # env_from=[ETL_CONFIG],
        # secrets=[ODS_SECRET, MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.sftp.extract.SFTPUnicodeTextFileExtractorTask'),
        do_xcom_push=False,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="extract_valid",
        get_logs=True,
    )

    EXTRACT_SEED_FILES = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="extract_major_professional_activity",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        # env_from=[ETL_CONFIG],
        # secrets=[ODS_SECRET, MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.s3.extract.S3FileExtractorTask'),
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="extract_seed_files",
        get_logs=True,
    )

    ASSIGN_EXISTING_CONTACT_IDS = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="create_physician_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        # env_from=[ETL_CONFIG],
        # secrets=[MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.contactid.transform.ContactIDMergeTransformerTask'),
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="assign_existing_contact_ids",
        get_logs=True,
    )

    MERGE_AND_GENERATE_NEW_IDS = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        name="create_type_of_practice_table",
        # env_from=[ETL_CONFIG],
        # secrets=[MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.contactid.transform.ContactIDMergeTransformerTask'),
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="merge_and_generate_new_ids",
        get_logs=True,
    )

    DELIVER_OUTPUT_FILES = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="load_tables_into_database",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        # env_from=[ETL_CONFIG],
        # secrets=[DATABASE_SECRET, MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.sftp.load.SFTPFileLoaderTask'),
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="deliver_output_files",
        get_logs=True,
    )

    UPDATE_SEED_FILES = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="load_tables_into_database",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        # env_from=[ETL_CONFIG],
        # secrets=[DATABASE_SECRET, MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.s3.load.S3FileLoaderTask'),
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="update_seed_files",
        get_logs=True,
    )


EXTRACT_VALID >> ASSIGN_EXISTING_CONTACT_IDS
EXTRACT_ADVANTAGE >> ASSIGN_EXISTING_CONTACT_IDS
EXTRACT_ORG_MANAGER >> ASSIGN_EXISTING_CONTACT_IDS
EXTRACT_SEED_FILES >> ASSIGN_EXISTING_CONTACT_IDS

ASSIGN_EXISTING_CONTACT_IDS >> MERGE_AND_GENERATE_NEW_IDS

MERGE_AND_GENERATE_NEW_IDS >> DELIVER_OUTPUT_FILES
MERGE_AND_GENERATE_NEW_IDS >> UPDATE_SEED_FILES
