package datalabs.etl.dag.lambda;

import java.util.Map;

import datalabs.task.Task;


public class DAGTaskWrapper extends datalabs.etl.dag.DAGTaskWrapper {
    public DAGTaskWrapper(Map<String, String> parameters) {
        super(parameters);
    }

    protected Map<String, String> getRuntimeParameters(Map<String, String> parameters) {
        /* TODO: FIXME
        String[] runtime = parameters.get(1).split("__", 3);
        String dag = runtime[0];
        String task = runtime[1];
        String execution_time = runtime[2];

        Map<String, String> runtimeParameters;
        runtimeParameters.put("dag", dag);
        runtimeParameters.put("task", task);
        runtimeParameters.put("execution_time", execution_time);
        */

        return runtimeParameters;
    }

    /* TODO: Port from Python

        def _handle_success(self) -> (int, dict):
            super()._handle_success()

            parameters = self._get_task_wrapper_parameters()

            if parameters.task == "DAG":
                for task in self.task.triggered_tasks:
                    self._notify_task_processor(task)
            else:
                state = self._get_plugin(self.DAG_PARAMETERS["DAG_STATE_CLASS"], parameters)

                success = state.set_task_status(parameters.dag, parameters.task, parameters.execution_time, Status.FINISHED)

                if not success:
                    LOGGER.error('Unable to set status of task %s of dag %s to Finished', parameters.task, parameters.dag)

                self._notify_dag_processor()

            return "Success"

        def _handle_exception(self, exception) -> (int, dict):
            super()._handle_exception(exception)

            parameters = self._get_task_wrapper_parameters()

            if parameters.task != "DAG":
                state = self._get_plugin(self.DAG_PARAMETERS["DAG_STATE_CLASS"], parameters)

                success = state.set_task_status(parameters.dag, parameters.task, parameters.execution_time, Status.FAILED)

                if not success:
                    LOGGER.error('Unable to set status of task %s of dag %s to Failed', parameters.task, parameters.dag)

                self._notify_dag_processor()

            LOGGER.exception(
                'An exception occured while attempting to run task %s of DAG %s.',
                self._get_task_id(),
                self._get_dag_id()
            )

            return f'Failed: {str(exception)}'
    */
}
