''' Masterfile OneView DAG definition. '''
from airflow import DAG
from airflow.kubernetes.secret import Secret
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s


### Configuration Bootstraping ###
DAG_ID = 'contact_id'
DEPLOYMENT_ID = Variable.get('DEPLOYMENT_ID')
IMAGE = Variable.get(f'{DAG_ID.upper()}_IMAGE')

### Kubernets Configuration ###
ETL_CONFIG = k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name='contact-id-etl'))
ADVANTAGE_SECRET = Secret('env', None, 'contact-id-etl-advantage')
ORGMANAGER_SECRET = Secret('env', None, 'contact-id-etl-orgmanager')
VALID_EFT_SECRET = Secret('env', None, 'contact-id-etl-valid')
MINIO_SECRET = Secret('env', None, 'contact-id-etl-minio')

### DAG definition ###
BASE_ENVIRONMENT = dict(
    TASK_WRAPPER_CLASS='datalabs.etl.airflow.task.AirflowTaskWrapper',
    ETCD_HOST=Variable.get('ETCD_HOST'),
    ETCD_USERNAME=DAG_ID,
    ETCD_PASSWORD=Variable.get(f'{DAG_ID.upper()}_ETCD_PASSWORD'),
    ETCD_PREFIX=f'{DAG_ID.upper()}_'
)

CONTACT_ID_ASSIGNMENT_DAG = DAG(
    dag_id=DAG_ID,
    default_args=dict(
        owner='airflow',
        resources=dict(
            limit_memory="8G",
            limit_cpu="1"
        ),
        is_delete_operator_pod=True,
        namespace=f'hsg-data-labs-{DEPLOYMENT_ID}',
        image=IMAGE,
        do_xcom_push=False,
        in_cluster=True,
        get_logs=True,
    ),
    schedule_interval=None,
    start_date=days_ago(2),
    tags=['ContactID'],
)


with CONTACT_ID_ASSIGNMENT_DAG:
    EXTRACT_ADVANTAGE = KubernetesPodOperator(
        name="extract_advantage",
        task_id="extract_advantage",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[ADVANTAGE_SECRET, MINIO_SECRET],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask')},
    )

    EXTRACT_ORG_MANAGER = KubernetesPodOperator(
        name="extract_org_manager",
        task_id="extract_org_manager",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[ORGMANAGER_SECRET, MINIO_SECRET],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask')},
    )

    EXTRACT_VALID = KubernetesPodOperator(
         name="extract_valid",
         task_id="extract_valid",
         cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
         env_from=[ETL_CONFIG],
         secrets=[VALID_EFT_SECRET, MINIO_SECRET],
         env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.sftp.extract.SFTPFileExtractorTask')},
     )

    EXTRACT_SEED_FILES = KubernetesPodOperator(
        name="extract_seed_files",
        task_id="extract_seed_files",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[MINIO_SECRET],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.s3.extract.S3FileExtractorTask')},
    )

    ASSIGN_EXISTING_CONTACT_IDS = KubernetesPodOperator(
        name="assign_existing_contact_ids",
        task_id="assign_existing_contact_ids",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.contactid.idassign.transform.ContactIDAssignTransformerTask'),
    )
    #
    MERGE_AND_GENERATE_NEW_IDS = KubernetesPodOperator(
        name="merge_and_generate_new_ids",
        task_id="merge_and_generate_new_ids",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.contactid.transform.ContactIDMergeTransformerTask'),
    )
    #
    DELIVER_OUTPUT_FILES = KubernetesPodOperator(
        name="deliver_output_files",
        task_id="deliver_output_files",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[VALID_EFT_SECRET, MINIO_SECRET],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.sftp.load.SFTPFileLoaderTask')},
     )

    UPDATE_SEED_FILES = KubernetesPodOperator(
        name="update_seed_files",
        task_id="update_seed_files",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[MINIO_SECRET],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.s3.load.S3FileLoaderTask')},
    )


#EXTRACT_VALID
EXTRACT_ADVANTAGE
EXTRACT_ORG_MANAGER
EXTRACT_SEED_FILE
#EXTRACT_VALID >> ASSIGN_EXISTING_CONTACT_IDS
#EXTRACT_ADVANTAGE >> ASSIGN_EXISTING_CONTACT_IDS
#EXTRACT_ORG_MANAGER >> ASSIGN_EXISTING_CONTACT_IDS
#EXTRACT_SEED_FILES >> ASSIGN_EXISTING_CONTACT_IDS
#ASSIGN_EXISTING_CONTACT_IDS >> MERGE_AND_GENERATE_NEW_IDS
#MERGE_AND_GENERATE_NEW_IDS >> DELIVER_OUTPUT_FILES
#MERGE_AND_GENERATE_NEW_IDS >> UPDATE_SEED_FILES
