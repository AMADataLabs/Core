""" Default CPT API endpoint class for invalid REST URLs. """
from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound


class DefaultEndpointTask(APIEndpointTask):
    # pylint: disable=no-self-use
    def run(self):
        # pylint: disable=no-self-use
        raise ResourceNotFound('Bad endpoint path')
