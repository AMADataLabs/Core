""" Resolve task class name using the API Gateway event passed to the Lambda function. """
from   collections import namedtuple
import re

from   datalabs.access.oneview.api.default import DefaultEndpointTask
from   datalabs.access.oneview.api.physician import PhysiciansEndpointTask
import datalabs.task as task


TaskClassMapping = namedtuple('TaskClassMapping', 'path task_class')

class TaskResolver(task.TaskResolver):
    # pylint: disable=line-too-long
    TASK_CLASSES = [
        TaskClassMapping('/physicians',             PhysiciansEndpointTask),
    ]

    @classmethod
    def get_task_class(cls, parameters):
        path = parameters['path']
        task_class = None

        for mapping in cls.TASK_CLASSES:
            path_pattern = mapping.path.replace('*', '[^/]+')

            if re.match(path_pattern, path):
                task_class = mapping.task_class
                break

        return task_class
