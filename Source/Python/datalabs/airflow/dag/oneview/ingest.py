import os

from   airflow import DAG
from   kubernetes.client import models as k8s
from   airflow.operators.python import PythonOperator
from   airflow.utils.dates import days_ago

from   datalabs.plugin import import_plugin


def task():
    task_class = import_plugin(os.environ['TASK_CLASS'])
    task_wrapper_class = import_plugin(os.environ['TASK_WRAPPER_CLASS'])
    task = task_wrapper_class(task_class)

    return task.run()


with DAG(
        dag_id='type_of_practice',
        default_args={'owner': 'airflow'},
        schedule_interval=None,
        start_date=days_ago(2),
        tags=['TypeOfPractice'],
) as dag:

    extractor = PythonOperator(
        task_id="type_of_practice_extractor",
        python_callable=task,
        executor_config={
            "pod_override": k8s.V1Pod(
                spec=k8s.V1PodSpec(
                    containers=[
                        k8s.V1Container(
                            name="base",
                            image="docker-registry.default.svc:5000/hsg-data-labs-dev/airflow-worker:1.0.0",
                            env=[
                                k8s.V1EnvFromSource(name="TASK_CLASS",
                                                    value="datalabs.etl.jdbc.extract.JDBCExtractorTask"
                                                    )
                            ],
                            env_var=[
                                k8s.V1EnvFromSource(
                                    config_map_ref=k8s.V1ConfigMapEnvSource(name='oneview-type-of-practice')
                                ),
                                k8s.V1EnvFromSource(
                                    secret_ref=k8s.V1ConfigMapEnvSource(name='aims-secret')
                                )
                            ]
                        )
                    ]
                )
            ),
        },
    )

    transformer = PythonOperator(
        task_id="type_of_practice_transformer",
        python_callable=task,
        executor_config={
            "pod_override": k8s.V1Pod(
                spec=k8s.V1PodSpec(
                    containers=[
                        k8s.V1Container(
                            name="base",
                            image="docker-registry.default.svc:5000/hsg-data-labs-dev/airflow-worker:1.0.0",
                            env=[
                                k8s.V1EnvFromSource(name="TASK_CLASS",
                                                    value="datalabs.etl.s3.load.S3UnicodeTextFileLoaderTask"
                                                    )
                            ],
                            env_var=[
                                k8s.V1EnvFromSource(
                                    config_map_ref=k8s.V1ConfigMapEnvSource(name='oneview-type-of-practice')
                                )
                            ]
                        )
                    ]
                )
            ),
        },
    )

    loader = PythonOperator(
        task_id="type_of_practice_loader",
        python_callable=task,
        executor_config={
            "pod_override": k8s.V1Pod(
                spec=k8s.V1PodSpec(
                    containers=[
                        k8s.V1Container(
                            name="base",
                            image="docker-registry.default.svc:5000/hsg-data-labs-dev/airflow-worker:1.0.0",
                            env=[
                                k8s.V1EnvFromSource(name="TASK_CLASS",
                                                    value="datalabs.etl.s3.load.S3UnicodeTextFileLoaderTask"
                                                    )
                            ],
                            env_var=[
                                k8s.V1EnvFromSource(
                                    config_map_ref=k8s.V1ConfigMapEnvSource(name='oneview-type-of-practice')
                                ),
                                k8s.V1EnvFromSource(
                                    secret_ref=k8s.V1ConfigMapEnvSource(name='minio-secret')
                                )
                            ]
                        )
                    ]
                )
            ),
        },
    )

extractor >> loader >> transformer
