''' Address Load Compiler DAG definition. '''
from   datalabs.analysis.address.batchload.transform import AddressLoadFileAggregationTransformerTask
from   datalabs.etl.dag import dag
from   datalabs.etl.sftp.extract import SFTPFileExtractorTask
from   datalabs.etl.sftp.load import SFTPFileLoaderTask


@dag.register(name="ADDRESS_LOAD_COMPILER")
class DAG(dag.DAG):
    EXTRACT_COMPONENT_FILES: SFTPFileExtractorTask
    COMPILE_BATCH_LOAD_FILE: AddressLoadFileAggregationTransformerTask
    LOAD_BATCH_LOAD_FILE: SFTPFileLoaderTask


# pylint: disable=pointless-statement
DAG.EXTRACT_COMPONENT_FILES >> DAG.COMPILE_BATCH_LOAD_FILE \
        >> DAG.LOAD_BATCH_LOAD_FILE
