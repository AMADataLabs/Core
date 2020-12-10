""" source: datalabs.access.environment """
import os
import pytest

from   gremlin_python.process.traversal import Bindings
from   neptune_python_utils.gremlin_utils import GremlinUtils


@pytest.mark.skipif(
    os.getenv('RUN_INTEGRATION_TESTS') != 'True',
    reason="Normally skip integration tests to increase testing speed."
)
def test_connection(lineage):
    lineage.V().hasLabel('dataset-test').outE().drop().iterate()
    lineage.V().hasLabel('dataset-test').drop().iterate()
    lineage.V().hasLabel('data-test').outE().drop().iterate()
    lineage.V().hasLabel('data-test').drop().iterate()

    raw_dataset = lineage.addV('dataset-test').property(
        'location', 's3://hsg-datalabs-datalake-ingestion-sandbox/AMA/BOGUS/20200131'
    ).next()

    pdf1 = lineage.addV('data-test').property(
        'location', 's3://ama-hsg-datalabs-datalake-ingestion-sandbox/AMA/BOGUS/20200131/'
                    'BOGUS Link Release Notes 20200131.pdf'
    ).next()

    pdf2 = lineage.addV('data-test').property(
        'location', 's3://ama-hsg-datalabs-datalake-ingestion-sandbox/AMA/BOGUS/20200131/'
                    'standard/AnesthesiaGuidelines.pdf'
    ).next()

    processed_dataset = lineage.addV('dataset-test').property(
        'location', 's3://hsg-datalabs-datalake-processed-sandbox/AMA/BOGUS/20200820'
    ).next()

    pdf_zip = lineage.addV('data-test').property(
        'location', 's3://ama-hsg-datalabs-datalake-processed-sandbox/AMA/BOGUS/20200820/pdfs.zip'
    ).next()

    lineage.V(Bindings.of('id', raw_dataset)).addE('ParentOf').to(processed_dataset).property(
        'timestamp', '20200820T21:38:32+00:00'
    ).iterate()

    lineage.V(Bindings.of('id', pdf1)).addE('ParentOf').to(pdf_zip).property(
        'timestamp', '20200820T21:38:32+00:00'
    ).iterate()

    lineage.V(Bindings.of('id', pdf2)).addE('ParentOf').to(pdf_zip).property(
        'timestamp', '20200820T21:38:32+00:00'
    ).iterate()

    lineage.V(Bindings.of('id', raw_dataset)).addE('Contains').to(pdf1).property(
        'timestamp', '20200820T21:38:32+00:00'
    ).iterate()

    lineage.V(Bindings.of('id', raw_dataset)).addE('Contains').to(pdf2).property(
        'timestamp', '20200820T21:38:32+00:00'
    ).iterate()

    lineage.V(Bindings.of('id', processed_dataset)).addE('Contains').to(pdf_zip).property(
        'timestamp', '20200820T21:38:32+00:00'
    ).iterate()

    assert len(lineage.V().hasLabel('dataset-test').toList()) == 2

    assert len(lineage.V().hasLabel('data-test').toList()) == 3

    edge_count = len(lineage.E().toList())

    lineage.V().hasLabel('dataset-test').outE().drop().iterate()
    assert len(lineage.E().toList()) == (edge_count - 4)

    lineage.V().hasLabel('data-test').outE().drop().iterate()
    assert len(lineage.E().toList()) == (edge_count - 6)

    lineage.V().hasLabel('dataset-test').drop().iterate()
    assert len(lineage.V().hasLabel('dataset-test').toList()) == 0

    lineage.V().hasLabel('data-test').drop().iterate()
    assert len(lineage.V().hasLabel('data-test').toList()) == 0


@pytest.fixture
def lineage():
    os.environ['NEPTUNE_CLUSTER_ENDPOINT'] = 'datalabs-lineage.cluster-c3mn4zysffxi.us-east-1.neptune.amazonaws.com'
    os.environ['NEPTUNE_CLUSTER_PORT'] = '8182'
    GremlinUtils.init_statics(globals())
    gremlin_utils = GremlinUtils()
    connection = gremlin_utils.remote_connection()
    # host = 'datalabs-lineage.cluster-c3mn4zysffxi.us-east-1.neptune.amazonaws.com'
    # connection = DriverRemoteConnection(f'wss://{host}:8182/gremlin','g')

    yield gremlin_utils.traversal_source(connection=connection)

    connection.close()
