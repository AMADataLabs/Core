''' Definition for the HelloWorldJava DAG. '''
from   datalabs.etl.dag.dag import DAG, register


@register(name="HELLO_WORLD_JAVA")
class HelloWorldJavaDAG(DAG):
    LOG_MESSAGE: "datalabs.example.etl.HelloWorldTask"
