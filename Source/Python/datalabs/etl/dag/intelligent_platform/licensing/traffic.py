''' DAG definition for the Intelligent Platform Licensing ETL. '''
import datalabs.etl.dag.dag as dag

from   datalabs.etl.sql.sqlalchemy.extract import SQLAlchemyExtractorTask
from   datalabs.etl.intelligent_platform.licensing.traffic.load import TrafficReportEmailLoaderTask


@dag.register(name="LICENSING")
class DAG(dag.DAG):
    EXTRACT_TRAFFIC: SQLAlchemyExtractorTask
    SEND_TRAFFIC_REPORT: TrafficReportEmailLoaderTask


# pylint: disable=pointless-statement
EXTRACT_TRAFFIC >> SEND_TRAFFIC_REPORT
