''' DAG definition for the DAG Scheduler. '''
from   datalabs.etl.dag.dag import DAG
from   datalabs.etl.archive.transform import ZipTransformerTask
from   datalabs.etl.cpt.release.transform import ReleaseTransformerTask
from   datalabs.etl.cpt.api.load import CPTRelationalTableLoaderTask
from   datalabs.etl.cpt.api.transform import CSVToRelationalTablesTransformerTask
from   datalabs.etl.cpt.ingest.extract import CPTTextDataExtractorTask
from   datalabs.etl.parse.transform import ParseToCSVTransformerTask

class OneViewDAG(DAG):
    GENERATE_RELEASE: ReleaseTransformerTask
    EXTRACT_TEXT_FILES: CPTTextDataExtractorTask
    PARSE_TEXT_FILES: ParseToCSVTransformerTask
    CREATE_TABLES: CSVToRelationalTablesTransformerTask
    CREATE_PDFS_ZIP: ZipTransformerTask
    LOAD_TABLES: CSVToRelationalTablesTransformerTask


OneViewDAG.EXTRACT_TEXT_FILES >> OneViewDAG.PARSE_TEXT_FILES >> OneViewDAG.CREATE_TABLES >> OneViewDAG.LOAD_TABLES
