''' Definition for the HelloWorldJava DAG. '''
from   datalabs.etl.dag.dag import DAG, register, JavaTask


@register(name="HELLO_WORLD_JAVA")
class HelloWorldJavaDAG(DAG):
    LOG_MESSAGE: JavaTask("datalabs.example.etl.HelloWorldTask")
