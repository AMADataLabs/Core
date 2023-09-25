''' Definition for the HelloWorld DAG. '''
from   datalabs.etl.dag.dag import DAG, register
from   datalabs.example.etl.hello_world.task import HelloWorldTask



@register(name="HELLO_WORLD")
class HelloWorldDAG(DAG):
    PRINT_HELLO_WORLD: HelloWorldTask
    PRINT_HELLO_WORLD1: HelloWorldTask
    PRINT_HELLO_WORLD2: HelloWorldTask
    PRINT_HELLO_WORLD3: HelloWorldTask

# pylint: disable=pointless-statement
HelloWorldDAG.PRINT_HELLO_WORLD >> HelloWorldDAG.PRINT_HELLO_WORLD1 >> HelloWorldDAG.PRINT_HELLO_WORLD2

HelloWorldDAG.PRINT_HELLO_WORLD >> HelloWorldDAG.PRINT_HELLO_WORLD3 >> HelloWorldDAG.PRINT_HELLO_WORLD2
