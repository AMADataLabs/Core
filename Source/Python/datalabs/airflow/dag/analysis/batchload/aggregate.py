''' Masterfile OneView DAG definition. '''
from airflow import DAG
from airflow.kubernetes.secret import Secret
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s


### Configuration Bootstraping ###
DAG_ID = 'address_load_aggregation'
DEPLOYMENT_ID = Variable.get('DEPLOYMENT_ID')
IMAGE = Variable.get(f'{DAG_ID.upper()}_IMAGE')

### Kubernets Configuration ###
ETL_CONFIG = k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name='address-load-aggregate'))
EFT_SECRET = Secret('env', None, 'analysis-etl-secret')

### DAG definition ###
BASE_ENVIRONMENT = dict(
    TASK_WRAPPER_CLASS='datalabs.etl.dag.task.DAGTaskWrapper'
)

ADDRESS_LOAD_AGGREGATION_DAG = DAG(
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
    schedule_interval=None,
    start_date=days_ago(2),
    tags=['ADDRESS_LOAD'],
)


with ADDRESS_LOAD_AGGREGATION_DAG:
    EXTRACT_ADDRESS_LOAD = KubernetesPodOperator(
        name="extract_address_load",
        task_id="extract_address_load",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[EFT_SECRET],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.sftp.extract.SFTPFileExtractorTask')},
    )

with ADDRESS_LOAD_AGGREGATION_DAG:
    TRANSFROM_ADDRESS_LOAD = KubernetesPodOperator(
        name="transform_address_load",
        task_id="transform_address_load",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[EFT_SECRET],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.analysis.address.batchload.transform.AddressLoadFileAggregationTransformerTask')},
    )

with ADDRESS_LOAD_AGGREGATION_DAG:
    LOADER_ADDRESS_LOAD = KubernetesPodOperator(
        name="loader_address_load",
        task_id="loader_address_load",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[EFT_SECRET],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.sftp.load.SFTPFileLoaderTask')},
    )

EXTRACT_ADDRESS_LOAD >> TRANSFROM_ADDRESS_LOAD >> LOADER_ADDRESS_LOAD