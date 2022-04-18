''' Masterfile OneView DAG definition. '''
from airflow import DAG
from airflow.kubernetes.secret import Secret
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s


### Configuration Bootstraping ###
DAG_ID = 'oneview_refresh_dev'
DEPLOYMENT_ID = Variable.get('DEPLOYMENT_ID')
IMAGE = Variable.get(f'{DAG_ID.upper()}_IMAGE')

BASE_ENVIRONMENT = dict(
    TASK_WRAPPER_CLASS='datalabs.etl.dag.task.DAGTaskWrapper'
)

### Kubernets Configuration ###
ETL_CONFIG = k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name='oneview-refresh'))
ETL_SECRETS = Secret('env', None, 'oneview-refresh-secrets')

### DAG definition ###
ONEVIEW_ETL_DAG = DAG(
    dag_id=DAG_ID,
    default_args=dict(
        owner='airflow',
        resources=dict(
            limit_memory="10G",
            limit_cpu="2"
        ),
        is_delete_operator_pod=True,
        namespace=f'hsg-data-labs-{DEPLOYMENT_ID}',
        image=IMAGE,
        do_xcom_push=False,
        in_cluster=True,
        get_logs=True,
    ),
    schedule_interval="0 20 * * 0",
    start_date=datetime(2021, 11, 30),
    tags=['OneView'],
)


with ONEVIEW_ETL_DAG:
    REFRESH_PHYSICIAN_VIEW = KubernetesPodOperator(
        name="refresh_physician_view",
        task_id="refresh_physician_view",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[ETL_SECRETS],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.orm.load.MaterializedViewRefresherTask')},
    )

    REINDEX_PHYSICIAN_VIEW = KubernetesPodOperator(
        name="reindex_physician_view",
        task_id="reindex_physician_view",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[ETL_SECRETS],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.orm.load.ReindexerTask')},
    )

    REFRESH_PROVIDER_VIEW = KubernetesPodOperator(
        name="refresh_provider_view",
        task_id="refresh_provider_view",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[ETL_SECRETS],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.orm.load.MaterializedViewRefresherTask')},
    )

    REINDEX_PROVIDER_VIEW = KubernetesPodOperator(
        name="reindex_provider_view",
        task_id="reindex_provider_view",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[ETL_SECRETS],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.orm.load.ReindexerTask')},
    )


REFRESH_PHYSICIAN_VIEW >> REINDEX_PHYSICIAN_VIEW >> REFRESH_PROVIDER_VIEW >> REINDEX_PROVIDER_VIEW
