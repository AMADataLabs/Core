""" Resolve task class name using the API Gateway event passed to the Lambda function. """
from   collections import namedtuple
import re

from   datalabs.access.cpt.api.bulk import FilesEndpointTask
import datalabs.access.cpt.api.clinician_descriptor as clinician_descriptor
import datalabs.access.cpt.api.consumer_descriptor as consumer_descriptor
from   datalabs.access.cpt.api.default import DefaultEndpointTask
from   datalabs.access.cpt.api.descriptor import DescriptorEndpointTask, AllDescriptorsEndpointTask
from   datalabs.access.cpt.api.modifier import ModifierEndpointTask, AllModifiersEndpointTask
from   datalabs.access.cpt.api.pdf import LatestPDFsEndpointTask
from   datalabs.access.cpt.api.pla import PLADetailsEndpointTask, AllPLADetailsEndpointTask
from   datalabs.access.cpt.api.release import ReleasesEndpointTask
import datalabs.task as task


TaskClassMapping = namedtuple('TaskClassMapping', 'path task_class')

class TaskResolver(task.TaskResolver):
    # pylint: disable=line-too-long
    TASK_CLASSES = [
        # Granular Endpoints
        TaskClassMapping('/descriptor/*',             DescriptorEndpointTask),
        TaskClassMapping('/descriptors',              AllDescriptorsEndpointTask),
        TaskClassMapping('/consumer/descriptor/*',    consumer_descriptor.ConsumerDescriptorEndpointTask),
        TaskClassMapping('/consumer/descriptors',     consumer_descriptor.AllConsumerDescriptorsEndpointTask),
        TaskClassMapping('/clinician/descriptors/*',  clinician_descriptor.ClinicianDescriptorsEndpointTask),
        TaskClassMapping('/clinician/descriptors',    clinician_descriptor.AllClinicianDescriptorsEndpointTask),
        TaskClassMapping('/pla/details/*',            PLADetailsEndpointTask),
        TaskClassMapping('/pla/details',              AllPLADetailsEndpointTask),
        TaskClassMapping('/modifier/*',               ModifierEndpointTask),
        TaskClassMapping('/modifiers',                AllModifiersEndpointTask),
        TaskClassMapping('/pdfs',                     LatestPDFsEndpointTask),
        TaskClassMapping('/releases',                 ReleasesEndpointTask),
        TaskClassMapping('/*',                        DefaultEndpointTask),

        # Bulk Endpoints
        TaskClassMapping('/files',           FilesEndpointTask)
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
