""" Default CPT API endpoint class for invalid REST URLs. """
from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound


class DefaultEndpointTask(APIEndpointTask):
    def _run(self, database):
        raise ResourceNotFound('Bad endpoint path')
