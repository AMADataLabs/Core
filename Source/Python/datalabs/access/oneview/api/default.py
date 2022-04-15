""" Default OneView content API endpoint class for invalid REST URLs. """
from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound


class DefaultEndpointTask(APIEndpointTask):
    # pylint: disable=no-self-use
    def _run(self):
        raise ResourceNotFound('Bad endpoint path')
