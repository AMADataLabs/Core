''' Address Load Compiler DAG definition. '''
from   datalabs.analysis.address.batchload.transform import AddressLoadFileAggregationTransformerTask
from   datalabs.etl.dag import dag
from   datalabs.etl.sftp.extract import SFTPFileExtractorTask
from   datalabs.etl.sftp.load import SFTPFileLoaderTask


@dag.register(name="ADDRESS_LOAD_COMPILER")
class DAG(dag.DAG):
    EXTRACT_ADDRESS_LOAD_COMPILER: SFTPFileExtractorTask
    TRANSFROM_ADDRESS_LOAD_COMPILER: AddressLoadFileAggregationTransformerTask
    LOAD_ADDRESS_LOAD_COMPILER: SFTPFileLoaderTask


# pylint: disable=pointless-statement
DAG.EXTRACT_ADDRESS_LOAD_COMPILER >> DAG.TRANSFROM_ADDRESS_LOAD_COMPILER \
        >> DAG.LOAD_ADDRESS_LOAD_COMPILER
