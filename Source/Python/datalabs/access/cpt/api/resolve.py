from   collections import namedtuple
import re


TaskClassMapping = namedtuple('TaskClassMapping', 'path class_name')

class TaskResolver:
    TASK_CLASSES = [
        TaskClassMapping('/descriptor/*',             'datalabs.access.cpt.api.descriptor.DescriptorEndpointTask'),
        TaskClassMapping('/descriptors',              'datalabs.access.cpt.api.descriptor.AllDescriptorsEndpointTask'),
        TaskClassMapping('/consumer/descriptor/*',    'datalabs.access.cpt.api.consumer_descriptor.ConsumerDescriptorEndpointTask'),
        TaskClassMapping('/consumer/descriptors',     'datalabs.access.cpt.api.consumer_descriptor.AllConsumerDescriptorsEndpointTask'),
        TaskClassMapping('/clinician/descriptors/*',  'datalabs.access.cpt.api.clinician_descriptor.ClinicianDescriptorsEndpointTask'),
        TaskClassMapping('/clinician/descriptors',    'datalabs.access.cpt.api.clinician_descriptor.AllClinicianDescriptorsEndpointTask'),
        TaskClassMapping('/pla/details/*',            'datalabs.access.cpt.api.pla.PLADetailsEndpointTask'),
        TaskClassMapping('/pla/details',              'datalabs.access.cpt.api.pla.AllPLADetailsEndpointTask'),
        TaskClassMapping('/modifier/*',               'datalabs.access.cpt.api.modifier.ModifierEndpointTask'),
        TaskClassMapping('/modifiers',                'datalabs.access.cpt.api.modifier.AllModifiersEndpointTask'),
        TaskClassMapping('/pdfs',                     'datalabs.access.cpt.api.pdf.LatestPDFsEndpointTask'),
        TaskClassMapping('/releases',                 'datalabs.access.cpt.api.release.ReleasesEndpointTask'),
        TaskClassMapping('/*',                        'datalabs.access.cpt.api.default.DefaultEndpointTask')
    ]

    @classmethod
    def get_task_class_name(cls, parameters):
        path = parameters['path']
        class_name = None

        for mapping in cls.TASK_CLASSES:
            path_pattern = mapping.path.replace('*', '[^/]+')

            if re.match(path_pattern, path):
                class_name = mapping.class_name
                break

        return class_name
