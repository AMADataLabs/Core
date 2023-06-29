""" Airflow DAG task wrapper """
import datalabs.etl.dag.task


class DAGTaskWrapper(datalabs.etl.dag.task.DAGTaskWrapper):
    def _get_dag_parameters(self):
        return self._parse_command_line_parameters(self._parameters)

    @classmethod
    def _parse_command_line_parameters(cls, command_line_parameters):
        dag, task, execution_time = command_line_parameters[1].split('__')

        return dict(
            dag=dag,
            task=task,
            execution_time=execution_time
        )
