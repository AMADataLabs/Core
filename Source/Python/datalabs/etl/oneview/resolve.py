""" Resolve task class name using the API Gateway event passed to the Lambda function. """
import datalabs.task as task
from   datalabs.plugin import import_plugin


class TaskResolver(task.TaskResolver):
    # pylint: disable=line-too-long
    DAG_CLASS = 'datalabs.etl.oneview.dag.OneViewDAG'

    @classmethod
    def get_task_class_name(cls, parameters):
        type = parameters['type']
        task = parameters.get('task')
        execution_time = parameters['execution_time']
        class_name = cls.DAG_CLASS


        if type == "DAG":
            pass
        elif type == "Task":
            dag_class = import_plugin(cls.DAG_CLASS)
            class_name = dag_class.TASK_CLASSES[task]
        else:
            raise ValueError(f"Invalid DAG plugin event type '{type}'")

        return class_name
