''' Masterfile OneView DAG definition. '''
from airflow import DAG
from airflow.kubernetes.secret import Secret
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s
from datetime import datetime


### Configuration Bootstraping ###
DAG_ID = 'license_movement'
DEPLOYMENT_ID = Variable.get('DEPLOYMENT_ID')
IMAGE = Variable.get(f'{DAG_ID.upper()}_IMAGE')

### Kubernets Configuration ###
ETL_CONFIG = k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name='license-movement-etl'))
EFT_SECRET = Secret('env', None, 'license-movement-etl-secret')

### DAG definition ###
BASE_ENVIRONMENT = dict(
    TASK_WRAPPER_CLASS='datalabs.etl.dag.task.DAGTaskWrapper'
)

LICENSE_MOVEMENT_DAG = DAG(
    dag_id=DAG_ID,
    default_args=dict(
        owner='airflow',
        resources=dict(
            limit_memory="8G",
            limit_cpu="1"
        ),
        is_delete_operator_pod=False,
        namespace=f'hsg-data-labs-{DEPLOYMENT_ID}',
        image=IMAGE,
        do_xcom_push=False,
        in_cluster=True,
        get_logs=True,
    ),
    schedule_interval="0 0 12 ? * WED",
    start_date=datetime(2021, 12, 4),
    tags=['LICENSE_MOVEMENT'],
    # catchup=True
)


with LICENSE_MOVEMENT_DAG:
    GET_PPD = KubernetesPodOperator(
        name="get_ppd",
        task_id="get_ppd",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[EFT_SECRET],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.sftp.extract.SFTPFileExtractorTask')},
    )

with LICENSE_MOVEMENT_DAG:
    GET_CREDENTIALING_DATA = KubernetesPodOperator(
        name="get_credentialing_data",
        task_id="get_credentialing_data",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[EFT_SECRET],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.sftp.extract.SFTPFileExtractorTask')},
    )

GET_PPD