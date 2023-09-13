''' DAG definition for the DAG Scheduler. '''
from   datalabs.etl.dag.dag import DAG
from   datalabs.example.etl.hello_world.task import HelloWorldTask


class SchedulerDAG(DAG):
    EXTRACT_SCHEDULES: HelloWorldTask
    IDENTIFY_SCHEDULED_DAGS: HelloWorldTask
    SCHEDULE_DAGS: HelloWorldTask
    EXTRACT_SCHEDULED_DAG_STATES: HelloWorldTask
    SEND_DAG_REPORT: HelloWorldTask


# pylint: disable=pointless-statement,undefined-variable
    SchedulerDAG.EXTRACT_SCHEDULES >> \
    SchedulerDAG.IDENTIFY_SCHEDULED_DAGS >> \
    SchedulerDAG.EXTRACT_SCHEDULED_DAG_STATES >> \
    SchedulerDAG.SEND_DAG_REPORT
