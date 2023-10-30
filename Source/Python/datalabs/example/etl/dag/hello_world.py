''' dynamic.datalabs.example.etl.dag.hello_world.HelloWorldDAG
    Definition for the HelloWorld DAG.
'''
from   datalabs.etl.dag.dag import DAG, register



@register(name="HELLO_WORLD")
class HelloWorldDAG(DAG):
    PRINT_HELLO_WORLD: "datalabs.example.etl.hello_world.task.HelloWorldTask"
    PRINT_HELLO_WORLD1: "datalabs.example.etl.hello_world.task.HelloWorldTask"
    PRINT_HELLO_WORLD2: "datalabs.example.etl.hello_world.task.HelloWorldTask"
    PRINT_HELLO_WORLD3: "datalabs.example.etl.hello_world.task.HelloWorldTask"
    # PRINT_HELLO_WORLD4: "datalabs.example.etl.hello_world.task.HelloWorldTask"
    # PRINT_HELLO_WORLD5: "datalabs.example.etl.hello_world.task.HelloWorldTask"

# pylint: disable=pointless-statement
HelloWorldDAG.PRINT_HELLO_WORLD >> HelloWorldDAG.PRINT_HELLO_WORLD1 >> HelloWorldDAG.PRINT_HELLO_WORLD2

HelloWorldDAG.PRINT_HELLO_WORLD >> HelloWorldDAG.PRINT_HELLO_WORLD3 >> HelloWorldDAG.PRINT_HELLO_WORLD2

# HelloWorldDAG.PRINT_HELLO_WORLD2 >> HelloWorldDAG.PRINT_HELLO_WORLD4
# HelloWorldDAG.PRINT_HELLO_WORLD2 >> HelloWorldDAG.PRINT_HELLO_WORLD5
