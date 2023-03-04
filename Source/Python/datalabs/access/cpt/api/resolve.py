""" Resolve task class name using the API Gateway event passed to the Lambda function. """
from   collections import namedtuple
import logging
import re

from   datalabs.access.cpt.api.bulk import FilesEndpointTask
from   datalabs.access.cpt.api import clinician_descriptor
from    datalabs.access.cpt.api import consumer_descriptor
from   datalabs.access.cpt.api.default import DefaultEndpointTask
from   datalabs.access.cpt.api.descriptor import DescriptorEndpointTask, AllDescriptorsEndpointTask
from   datalabs.access.cpt.api.modifier import ModifierEndpointTask, AllModifiersEndpointTask
from   datalabs.access.cpt.api.pdf import LatestPDFsEndpointTask
from   datalabs.access.cpt.api.pla import PLADetailsEndpointTask, AllPLADetailsEndpointTask
from   datalabs.access.cpt.api.release import ReleasesEndpointTask
from   datalabs import task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


TaskClassMapping = namedtuple('TaskClassMapping', 'path task_class')
TaskIDMapping = namedtuple('TaskIdMapping', 'path task_id')

class TaskResolver(task.TaskResolver):
    TASK_CLASSES = [
        # JSON Endpoints
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

        # Zip Endpoints
        TaskClassMapping('/bulk_zip/releases',        ReleasesEndpointTask),
        TaskClassMapping('/bulk_zip/files',           FilesEndpointTask),

        # Default Endpoint (Must be the last endpoint in this list)
        TaskClassMapping('/*',                        DefaultEndpointTask)
    ]

    TASK_IDS = [
        # JSON Endpoints
        TaskClassMapping('/descriptor/*',             "DESCRIPTOR"),
        TaskClassMapping('/descriptors',              "DESCRIPTORS"),
        TaskClassMapping('/consumer/descriptor/*',    "CONSUMER_DESCRIPTOR"),
        TaskClassMapping('/consumer/descriptors',     "CONSUMER_DESCRIPTORS"),
        TaskClassMapping('/clinician/descriptors/*',  "CLINICIAN_DESCRIPTORS"),
        TaskClassMapping('/clinician/descriptors',    "ALL_CLINICIAN_DESCRIPTORS"),
        TaskClassMapping('/pla/details/*',            "PLA_DETAILS"),
        TaskClassMapping('/pla/details',              "ALL_PLA_DETAILS"),
        TaskClassMapping('/modifier/*',               "MODIFIER"),
        TaskClassMapping('/modifiers',                "MODIFIERS"),
        TaskClassMapping('/pdfs',                     "PDFS"),
        TaskClassMapping('/releases',                 "RELEASES"),

        # Zip Endpoints
        TaskClassMapping('/bulk_zip/releases',        "RELEASES"),
        TaskClassMapping('/bulk_zip/files',           "FILES"),

        # Default Endpoint (Must be the last endpoint in this list)
        TaskClassMapping('/*',                        "DEFAULT")
    ]

    @classmethod
    def get_task_class(cls, runtime_parameters):
        path = runtime_parameters['path']
        task_class = None

        for mapping in cls.TASK_CLASSES:
            path_pattern = mapping.path.replace('*', '[^/]+')

            if re.match(path_pattern, path):
                task_class = mapping.task_class
                break
        LOGGER.info('Resolved path %s to implementation class %s', path, str(task_class))

        return task_class

    @classmethod
    def get_task_id(cls, runtime_parameters):
        path = runtime_parameters['path']
        task_id = None

        for mapping in cls.TASK_IDS:
            path_pattern = mapping.path.replace('*', '[^/]+')

            if re.match(path_pattern, path):
                task_id = mapping.task_id
                break
        LOGGER.info('Resolved path %s to implementation ID %s', path, str(task_id))

        return task_id
