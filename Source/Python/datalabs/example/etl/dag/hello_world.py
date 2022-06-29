''' Definition for the HelloWorld DAG. '''
from   datalabs.etl.dag.dag import DAG
from   datalabs.etl.task import DummyTask
from   datalabs.example.etl.hello_world.task import HelloWorldTask



class HelloWorldDAG(DAG):
    DUMMY_EXTRACTOR: DummyTask
    HELLO_WORLD_TRANSFORMER: HelloWorldTask
    DUMMY_LOADER: DummyTask

# pylint: disable=pointless-statement
HelloWorldDAG.DUMMY_EXTRACTOR >> HelloWorldDAG.HELLO_WORLD_TRANSFORMER >> HelloWorldDAG.DUMMY_LOADER
