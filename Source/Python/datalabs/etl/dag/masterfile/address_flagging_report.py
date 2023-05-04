''' AMC address flagging DAG definition. '''
from   datalabs.etl.dag import dag, JavaTask


@dag.register(name="ADDRESS_FLAGGING_REPORT")
class DAG(dag.DAG):
    EXTRACT_AMC: JavaTask("datalabs.etl.sql.SqlExtractorTask")
    FLAG_ADDRESSES: "datalabs.analysis.amc.transform.AMCAddressFlaggingTransformerTask"
    EMAIL_ADDRESS_REPORT: "datalabs.analysis.amc.load.AMCReportSMTPLoaderTask"


# pylint: disable=pointless-statement
DAG.EXTRACT_AMC >> DAG.FLAG_ADDRESSES >> DAG.EMAIL_ADDRESS_REPORT
