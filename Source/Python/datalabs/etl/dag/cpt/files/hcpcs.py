''' DAG definition for the DAG Scheduler. '''
from   datalabs.etl.dag.dag import DAG
from   datalabs.etl.archive.transform import UnzipTransformerTask
from   datalabs.etl.cpt.hcpcs.extract import HCPCSQuarterlyUpdateReportURLExtractorTask
from   datalabs.etl.http.extract import HTTPFileListExtractorTask


class HCPCSDAG(DAG):
    SCRAPE_HCPCS_REPORTS: HCPCSQuarterlyUpdateReportURLExtractorTask
    EXTRACT_HCPCS_REPORT: HTTPFileListExtractorTask
    UNZIP_HCPCS_REPORTS: UnzipTransformerTask


# pylint: disable=pointless-statement
HCPCSDAG.SCRAPE_HCPCS_REPORTS >> HCPCSDAG.EXTRACT_HCPCS_REPORT >> HCPCSDAG.UNZIP_HCPCS_REPORTS
