''' Masterfile OneView DAG definition. '''
from airflow import DAG
from airflow.kubernetes.secret import Secret
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s


### Configuration Bootstraping ###
DAG_ID = 'dbl'
DEPLOYMENT_ID = Variable.get('DEPLOYMENT_ID')
IMAGE = Variable.get(f'{DAG_ID.upper()}_IMAGE')

### Kubernets Configuration ###
ETL_CONFIG = k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name='report-etl'))
EFT_SECRET = Secret('env', None, 'dbl-etl-report')

### DAG definition ###
BASE_ENVIRONMENT = dict(
    TASK_WRAPPER_CLASS='datalabs.etl.dag.task.DAGTaskWrapper',
    ETCD_HOST=Variable.get('ETCD_HOST'),
    ETCD_USERNAME=DAG_ID,
    ETCD_PASSWORD=Variable.get(f'{DAG_ID.upper()}_ETCD_PASSWORD'),
    ETCD_PREFIX=f'{DAG_ID.upper()}_'
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
    schedule_interval=None,
    start_date=days_ago(2),
    tags=['DBL_Report'],
)


with DBL_REPORT_DAG:

    DBL_REPORT_EXTRACTOR = KubernetesPodOperator(
        name="dbl_extractor",
        task_id="dbl_extractor",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[EFT_SECRET],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.sftp.extract.SFTPFileExtractorTask')},
    )

    DBL_REPORT_TRANSFORMER = KubernetesPodOperator(
        name="dbl_transformer",
        task_id="dbl_transformer",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[EFT_SECRET],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.analysis.dbl.transform.DBLReportTransformer')},
    )

    DBL_REPORT_LOADER = KubernetesPodOperator(
        name="dbl_loader",
        task_id="dbl_loader",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[EFT_SECRET],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.analysis.dbl.load.DBLReportEmailLoaderTask')},
    )



#EXTRACT_VALID
#EXTRACT_ADVANTAGE
#EXTRACT_ORGMANAGER
#EXTRACT_SEED_FILES

DBL_REPORT_EXTRACTOR >> DBL_REPORT_TRANSFORMER >> DBL_REPORT_LOADER