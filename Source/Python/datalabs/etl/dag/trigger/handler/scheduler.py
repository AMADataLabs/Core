from   datalabs.etl.dag.trigger.resolve import register
from   datalabs.etl.dag.trigger.handler import task

@register(name="DAG_SCHEDULER")
class HandlerTask(task.HandlerTask):
    pass
