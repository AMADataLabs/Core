''' DAG definition for the Intelligent Platform Licensing ETL. '''
from   datalabs.etl.dag import dag
from   datalabs.etl.sql.sqlalchemy.extract import SQLAlchemyExtractorTask
from   datalabs.etl.intelligent_platform.licensing.traffic.load import TrafficReportSMTPLoaderTask


@dag.register(name="LICENSING_TRAFFIC")
class DAG(dag.DAG):
    EXTRACT_TRAFFIC: SQLAlchemyExtractorTask
    SEND_TRAFFIC_REPORT: TrafficReportSMTPLoaderTask


# pylint: disable=pointless-statement
DAG.EXTRACT_TRAFFIC >> DAG.SEND_TRAFFIC_REPORT
