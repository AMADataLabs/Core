from datalabs.access.awslambda import APIEndpointTaskWrapper


APIEndpointTaskWrapper.register_task('datalabs.access.cpt.api.descriptor.DescriptorEndpointTask')
APIEndpointTaskWrapper.register_task('datalabs.access.cpt.api.descriptor.AllDescriptorsEndpointTask')
