''' DAG definition for the DAG Scheduler. '''
from   datalabs.etl.dag import dag
from   datalabs.example.etl.hello_world.task import HelloWorldTask


@dag.register(name="DAG_REPORT")
class DAG(dag.DAG):
    EXTRACT_SCHEDULE: HelloWorldTask
    IDENTIFY_SCHEDULED_DAGS: HelloWorldTask
    EXTRACT_SCHEDULED_DAG_STATES: HelloWorldTask
    SEND_DAG_REPORT: HelloWorldTask


# pylint: disable=pointless-statement
DAG.EXTRACT_SCHEDULE \
    >> DAG.IDENTIFY_SCHEDULED_DAGS \
    >> DAG.EXTRACT_SCHEDULED_DAG_STATES \
    >> DAG.SEND_DAG_REPORT
