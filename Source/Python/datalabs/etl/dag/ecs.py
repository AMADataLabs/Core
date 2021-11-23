""" Task Wrapper for DAG plugins running in ECS """
import json

import datalabs.etl.dag.awslambda as awslambda


class ProcessorTaskWrapper(awslambda.ProcessorTaskWrapper):
    def _get_runtime_parameters(self, parameters):
        return json.loads(parameters[1])
