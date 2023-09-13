''' DAG definition for the DAG Scheduler. '''
from   datalabs.etl.dag.dag import DAG
from   datalabs.example.etl.hello_world.task import HelloWorldTask


class DAG(DAG):
    EXTRACT_SCHEDULE: HelloWorldTask
    SCHEDULE_DAGS: HelloWorldTask
    NOTIFY_DAG_PROCESSOR: HelloWorldTask


# pylint: disable=pointless-statement,undefined-variable
    DAG.EXTRACT_SCHEDULE >> \
    DAG.SCHEDULE_DAGS >> \
    DAG.NOTIFY_DAG_PROCESSOR
