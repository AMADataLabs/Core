""" Task Wrapper for DAG plugins running in ECS """
import json

import datalabs.etl.dag.awslambda as awslambda


class DAGTaskWrapper(awslambda.DAGTaskWrapper):
    def _get_runtime_parameters(self, parameters):
        if "task" not in event_parameters:
            event_parameters["task"] = "DAG"

        return json.loads(parameters[0])
