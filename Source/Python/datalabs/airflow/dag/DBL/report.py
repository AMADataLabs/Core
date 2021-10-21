''' Masterfile OneView DAG definition. '''
from airflow import DAG
from airflow.kubernetes.secret import Secret
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s
from datetime import datetime


### Configuration Bootstraping ###
DAG_ID = 'dbl'
DEPLOYMENT_ID = Variable.get('DEPLOYMENT_ID')
IMAGE = Variable.get(f'{DAG_ID.upper()}_IMAGE')

### Kubernets Configuration ###
ETL_CONFIG = k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name='dbl-file-count'))
EFT_SECRET = Secret('env', None, 'dbl-file-count-eft')

### DAG definition ###
BASE_ENVIRONMENT = dict(
    TASK_WRAPPER_CLASS='datalabs.etl.dag.task.DAGTaskWrapper'
)

DBL_REPORT_DAG = DAG(
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
    schedule_interval="0 20 * * 0",
    start_date=datetime(year=2021, month=9, day=25),
    tags=['DBL_Report'],
    catchup=True
)


with DBL_REPORT_DAG:
    EXTRACT_DBL = KubernetesPodOperator(
        name="extract_dbl",
        task_id="extract_dbl",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[EFT_SECRET],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.sftp.extract.SFTPFileExtractorTask')},
    )

    CREATE_DBL_REPORT = KubernetesPodOperator(
        name="create_dbl_report",
        task_id="create_dbl_report",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[EFT_SECRET],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.analysis.dbl.transform.DBLReportTransformer')},
    )

    EMAIL_DBL_REPORT = KubernetesPodOperator(
        name="email_dbl_report",
        task_id="email_dbl_report",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[EFT_SECRET],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.analysis.dbl.load.DBLReportEmailLoaderTask')},
    )

EXTRACT_DBL >> CREATE_DBL_REPORT >> EMAIL_DBL_REPORT
