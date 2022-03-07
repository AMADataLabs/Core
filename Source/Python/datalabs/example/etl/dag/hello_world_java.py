''' Definition for the HelloWorldJava DAG. '''
from   datalabs.etl.dag.dag import DAG


class HelloWorldJavaDAG(DAG):
    LOG_MESSAGE: "HelloWorldTask"
