''' Definition for the HelloWorld DAG. '''
from   datalabs.etl.dag.dag import DAG
from   datalabs.example.etl.hello_world.task import HelloWorldTask



class HelloWorldDAG(DAG):
    PRINT_HELLO_WORLD: HelloWorldTask

# pylint: disable=pointless-statement
HelloWorldDAG.PRINT_HELLO_WORLD
