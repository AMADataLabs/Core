''' DAG definition for License Movement Process '''
from   datalabs.etl.dag import dag
#from   datalabs.etl.dag.dag import register, Repeat
from   datalabs.etl.dag.dag import register


@register(name="LICENSE_MOVEMENT")
class DAG(dag.DAG):
    EXTRACT_PPD: "datalabs.etl.sftp.extract.SFTPFileExtractorTask"
    EXTRACT_CREDENTIALING_ADDRESSES: "datalabs.etl.sftp.extract.SFTPFileExtractorTask"
    EXTRACT_OLD_PPMA: "datalabs.etl.sql.extract.SQLExtractorTask"
    #EXTRACT_OLD_PPMA: Repeat("datalabs.etl.sql.SqlExtractorTask", 2)
    #CONCATENATE_OLD_PPMA: "datalabs.etl.manipulate.transform.ConcatenateTransformerTask"
    EXTRACT_MISMATCHES: "datalabs.etl.sql.extract.SQLExtractorTask"
    #EXTRACT_MISMATCHES: Repeat("datalabs.etl.sql.SqlExtractorTask", 12)
    #CONCATENATE_MISMATCHES: "datalabs.etl.manipulate.transform.ConcatenateTransformerTask"
    CREATE_BATCH_LOAD_FILE: "datalabs.analysis.ppma.license_movement.transform.LicenseMovementTransformerTask"
    LOAD_BATCH_LOAD_FILE: "datalabs.etl.sftp.load.SFTPFileLoaderTask"


# pylint: disable=pointless-statement, expression-not-assigned
DAG.EXTRACT_PPD >> DAG.CREATE_BATCH_LOAD_FILE
DAG.EXTRACT_CREDENTIALING_ADDRESSES >> DAG.CREATE_BATCH_LOAD_FILE
DAG.EXTRACT_OLD_PPMA >> DAG.CREATE_BATCH_LOAD_FILE
#DAG.sequence('EXTRACT_OLD_PPMA')
#DAG.last('EXTRACT_OLD_PPMA') \
#        >> DAG.CONCATENATE_OLD_PPMA \
#        >> DAG.CREATE_BATCH_LOAD_FILE
DAG.EXTRACT_MISMATCHES >> DAG.CREATE_BATCH_LOAD_FILE
#DAG.sequence('EXTRACT_MISMATCHES')
#DAG.last('EXTRACT_MISMATCHES') \
#        >> DAG.CONCATENATE_MISMATCHES \
#        >> DAG.CREATE_BATCH_LOAD_FILE
DAG.CREATE_BATCH_LOAD_FILE >> DAG.LOAD_BATCH_LOAD_FILE
