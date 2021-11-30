""" Task Wrapper for DAG plugins running in ECS """
import json

import datalabs.etl.dag.awslambda as awslambda


class DAGTaskWrapper(awslambda.DAGTaskWrapper):
    def _get_runtime_parameters(self, parameters):
        return super()._get_runtime_parameters(json.loads(parameters[0]))
