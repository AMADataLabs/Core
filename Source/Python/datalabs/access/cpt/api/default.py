""" Default CPT API endpoint class for invalid REST URLs. """
from   datalabs.access.task import APIEndpointTask, ResourceNotFound


class DefaultEndpointTask(APIEndpointTask):
    def _run(self, session):
        raise ResourceNotFound('Bad endpoint path')
