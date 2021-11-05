''' DAG definition for the DAG Scheduler. '''
from   datalabs.etl.dag.dag import DAG
from   datalabs.etl.archive.transform import UnzipTransformerTask
from   datalabs.etl.cpt.hcpcs.extract import HCPCSListingExtractorTask
from   datalabs.etl.http.extract import HTTPFileExtractorTask


class HCPCSDAG(DAG):
    SCRAPE_HCPCS_REPORTS: HCPCSListingExtractorTask
    EXTRACT_HCPCS_REPORT: HTTPFileExtractorTask
    UNZIP_HCPCS_REPORTS: UnzipTransformerTask


# pylint: disable=pointless-statement
HCPCSDAG.SCRAPE_HCPCS_REPORTS >> HCPCSDAG.EXTRACT_HCPCS_REPORT >> HCPCSDAG.UNZIP_HCPCS_REPORTS
