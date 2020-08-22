import pytest

from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal


def test_connection(lineage):
    raw_dataset = lineage.addV('dataset').property(
        'uid', 'f90dah024r90-fhd80ap8y4-hfd8p89r'
    ).property(
        'location', 's3://hsg-datalabs-datalake-ingestion-sandbox/AMA/CPT/20200131'
    ).next()

    pdf1 = lineage.addV('data').property(
        'uid', 'vsf0hq08-fh9r0wfurw0-f8w9ahpfr89'
    ).property(
        'location', 's3://ama-hsg-datalabs-datalake-ingestion-sandbox/AMA/CPT/20200131/CPT Link Release Notes 20200131.pdf'
    ).next()

    pdf2 = lineage.addV('data').property(
        'uid', 'hv8daphf8r9-nv8r9a8r7-vnr89ahr8'
    ).property(
        'location', 's3://ama-hsg-datalabs-datalake-ingestion-sandbox/AMA/CPT/20200131/standard/AnesthesiaGuidelines.pdf'
    ).next()

    processed_dataset = lineage.addV('dataset').property(
        'uid', 'vf80eaphgr989-hf8e9ahgr89e-hgf89eagr89'
    ).property(
        'location', 's3://hsg-datalabs-datalake-processed-sandbox/AMA/CPT/20200820'
    ).next()

    pdf_zip = lineage.addV('data').property(
        'uid', 'hfd890ahf89p-hf8dphf8-h8f9ah8fr9w'
    ).property(
        'location', 's3://ama-hsg-datalabs-datalake-processed-sandbox/AMA/CPT/20200820/pdfs.zip'
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

    lineage.V(Bindings.of('id', raw_dataset)).addE('ParentOf').to(pdf2).property(
        'timestamp', '20200820T21:38:32+00:00'
    ).iterate()

    lineage.V(Bindings.of('id', processed_dataset)).addE('Contains').to(pdf_zip).property(
        'timestamp', '20200820T21:38:32+00:00'
    ).iterate()

@pytest.fixture
def lineage():
    host = 'datalabs-lineage.cluster-c3mn4zysffxi.us-east-1.neptune.amazonaws.com'
    connection = DriverRemoteConnection(f'wss://{host}:8182/gremlin','g')

    yield traversal().withRemote(connection)

    connection.close()
