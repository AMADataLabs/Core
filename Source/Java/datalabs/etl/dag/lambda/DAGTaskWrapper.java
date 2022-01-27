package datalabs.etl.dag.lambda;

import java.util.Map;

import datalabs.task.Task;


/*
@add_schema(unknowns=True)
@dataclass
class DAGTaskWrapperParameters:
    dag: str
    task: str
    execution_time: str
    unknowns: dict=None
*/

public class DAGTaskWrapper extends datalabs.etl.dag.DAGTaskWrapper {
    public DAGTaskWrapper(Map<String, String> parameters) {
        super(parameters);
    }

    protected getDAGTaskParametersFromDynamoDB(String dag, String task) {
    /*
        @classmethod
        def _get_dag_task_parameters_from_dynamodb(cls, dag: str, task: str):
            parameters = {}

            dynamodb_loader = DynamoDBEnvironmentLoader(dict(
                table=os.environ["DYNAMODB_CONFIG_TABLE"],
                dag=dag,
                task=task
            ))
            dynamodb_loader.load(environment=parameters)

            return parameters
    */
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

        /*
        LOGGER.info('Event Parameters: %s', parameters)
        cls.DAG_PARAMETERS = cls._get_dag_task_parameters_from_dynamodb(parameters["dag"], "DAG")

        parameters["dag_class"] = cls.DAG_PARAMETERS["DAG_CLASS"]

        if "task" not in parameters:
            parameters["task"] = "DAG"

        return parameters
        */

        return runtimeParameters;
    }

    protected void preRun() {
        // super()._pre_run()
        //
        // parameters = self._get_task_wrapper_parameters()
        //
        // if parameters.task != "DAG":
        //     state = self._get_plugin(self.DAG_PARAMETERS["DAG_STATE_CLASS"], parameters)
        //
        //     state.set_task_status(parameters.dag, parameters.task, parameters.execution_time, Status.RUNNING)
    }

    protected String handleSuccess() {
        // super()._handle_success()
        //
        // parameters = self._get_task_wrapper_parameters()
        //
        // if parameters.task == "DAG":
        //     for task in self.task.triggered_tasks:
        //         self._notify_task_processor(task)
        // else:
        //     state = self._get_plugin(self.DAG_PARAMETERS["DAG_STATE_CLASS"], parameters)
        //
        //     success = state.set_task_status(parameters.dag, parameters.task, parameters.execution_time, Status.FINISHED)
        //
        //     if not success:
        //         LOGGER.error('Unable to set status of task %s of dag %s to Finished', parameters.task, parameters.dag)
        //
        //     self._notify_dag_processor()
        //
        // return "Success"

    }

    protected String handleException(Exception exception) {
        // super()._handle_exception(exception)
        //
        // parameters = self._get_task_wrapper_parameters()
        //
        // if parameters.task != "DAG":
        //     state = self._get_plugin(self.DAG_PARAMETERS["DAG_STATE_CLASS"], parameters)
        //
        //     success = state.set_task_status(parameters.dag, parameters.task, parameters.execution_time, Status.FAILED)
        //
        //     if not success:
        //         LOGGER.error('Unable to set status of task %s of dag %s to Failed', parameters.task, parameters.dag)
        //
        //     self._notify_dag_processor()
        //
        // LOGGER.exception(
        //     'An exception occured while attempting to run task %s of DAG %s.',
        //     self._get_task_id(),
        //     self._get_dag_id()
        // )
        //
        // return f'Failed: {str(exception)}'
    }

    protected Map<String, String> getDAGTaskParameters() {
        // dag = self._get_dag_id()
        // task = self._get_task_id()
        // LOGGER.debug('Getting DAG Task Parameters for %s__%s...', dag, task)
        // dag_task_parameters = self._get_dag_task_parameters_from_dynamodb(dag, task)
        // LOGGER.debug('Raw DAG Task Parameters: %s', dag_task_parameters)
        //
        // if task == 'DAG':
        //     dag_task_parameters["dag"] = dag
        // elif "LAMBDA_FUNCTION" in dag_task_parameters:
        //     dag_task_parameters.pop("LAMBDA_FUNCTION")
        // LOGGER.debug('Final DAG Task Parameters: %s', dag_task_parameters)
        //
        // return dag_task_parameters

    }

    Map<String, String> getTaskWrapperParameters() {
        // parameters = self._runtime_parameters
        // parameters.update(self.DAG_PARAMETERS)
        // parameters = self._get_validated_parameters(parameters)
        //
        // return parameters
    }

    void notifyTaskProcessor(Task task) {
        // task_topic = self._runtime_parameters["TASK_TOPIC_ARN"]
        // notifier = SNSTaskNotifier(task_topic)
        //
        // notifier.notify(self._get_dag_id(), task, self._get_execution_time())
    }

    void notifyDAGProcessor() {
        // dag_topic = self._runtime_parameters["DAG_TOPIC_ARN"]
        // notifier = SNSDAGNotifier(dag_topic)
        //
        // notifier.notify(self._get_dag_id(), self._get_execution_time())
    }
}
