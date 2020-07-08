from datalabs.access.awslambda import APIEndpointTaskWrapper


APIEndpointTaskWrapper.register_task('datalabs.access.cpt.api.descriptor.DescriptorEndpointTask')
APIEndpointTaskWrapper.register_task('datalabs.access.cpt.api.descriptor.AllDescriptorsEndpointTask')
APIEndpointTaskWrapper.register_task('datalabs.access.cpt.api.consumer_descriptor.ConsumerDescriptorEndpointTask')
APIEndpointTaskWrapper.register_task('datalabs.access.cpt.api.consumer_descriptor.AllConsumerDescriptorsEndpointTask')
APIEndpointTaskWrapper.register_task('datalabs.access.cpt.api.clinician_descriptor.ClinicianDescriptorsEndpointTask')
APIEndpointTaskWrapper.register_task('datalabs.access.cpt.api.clinician_descriptor.AllClinicianDescriptorsEndpointTask')
