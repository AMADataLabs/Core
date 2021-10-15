''' DAG definition for the DAG Scheduler. '''
from   datalabs.etl.dag.dag import DAG
from   datalabs.etl.archive.transform import ZipTransformerTask
from   datalabs.etl.cpt.release.transform import ReleaseTransformerTask, ReleaseTypesTransformerTask
from   datalabs.etl.cpt.api.load import CPTRelationalTableLoaderTask
from   datalabs.etl.cpt.api.transform import ReleasesTransformerTask, CSVToRelationalTablesTransformerTask
from   datalabs.etl.cpt.ingest.extract import CPTTextDataExtractorTask
from   datalabs.etl.orm.load import ORMLoaderTask
from   datalabs.etl.parse.transform import ParseToCSVTransformerTask


class CPTDAG(DAG):
    CREATE_CURRENT_RELEASE: ReleaseTransformerTask
    CREATE_RELEASE_TYPES: ReleaseTypesTransformerTask
    LOAD_RELEASE_TYPES: ORMLoaderTask
    PARSE_TEXT_FILES: ParseToCSVTransformerTask
    CREATE_RELEASES: ReleasesTransformerTask
    CREATE_PDFS_ZIP: ZipTransformerTask
    LOAD_TABLES: ORMLoaderTask
    LOAD_TABLES: ORMLoaderTask


CPTDAG.CREATE_RELEASE_TYPES >> CPTDAG.LOAD_RELEASE_TYPES

CPTDAG.CREATE_CURRENT_RELEASE >> CPTDAG.???
CPTDAG.PARSE_TEXT_FILES >> CPTDAG.CREATE_RELEASES

CPTDAG.CREATE_RELEASES >> CPTDAG.LOAD_DESCRIPTOR_TABLES
CPTDAG.LOAD_RELEASE_TYPES >> CPTDAG.LOAD_DESCRIPTOR_TABLES
