''' Masterfile OneView DAG definition. '''
from airflow import DAG
from airflow.kubernetes.secret import Secret
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s


### Configuration Bootstraping ###
DAG_ID = 'amc'
DEPLOYMENT_ID = Variable.get('DEPLOYMENT_ID')
IMAGE = Variable.get(f'{DAG_ID.upper()}_IMAGE')

### Kubernets Configuration ###
ETL_CONFIG = k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name='amc-address-flagging-report'))
AIMS_SECRET = Secret('env', None, 'amc-address-flagging-report')

### DAG definition ###
BASE_ENVIRONMENT = dict(
    TASK_WRAPPER_CLASS='datalabs.etl.dag.task.DAGTaskWrapper'
)

AMC_ADDRESS_FLAGGING_REPORT_DAG = DAG(
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
    tags=['Address_Flagging_Report'],
)


with AMC_ADDRESS_FLAGGING_REPORT_DAG:

    EXTRACT_AMC = KubernetesPodOperator(
        name="extract_amc",
        task_id="extract_amc",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[AIMS_SECRET],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask')},
    )

    FLAG_ADDRESSES = KubernetesPodOperator(
        name="flag_address_amc",
        task_id="flag_address_amc",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[AIMS_SECRET],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.analysis.amc.transform.AMCAddressFlaggingTransformerTask')},
    )

    EMAIL_ADDRESS_REPORT = KubernetesPodOperator(
        name="email_amc_report",
        task_id="email_amc_report",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[AIMS_SECRET],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.analysis.amc.load.AMCReportSMTPLoaderTask')},
    )



#EXTRACT_VALID
#EXTRACT_ADVANTAGE
#EXTRACT_ORGMANAGER
#EXTRACT_SEED_FILES

EXTRACT_AMC >> FLAG_ADDRESS_AMC >> EMAIL_AMC_REPORT
