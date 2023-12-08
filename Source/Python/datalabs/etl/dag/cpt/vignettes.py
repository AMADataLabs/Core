''' DAG definition for CPT Vignettes API ETL '''
from   datalabs.etl.dag import dag


@dag.register(name="CPT_VIGNETTES_ETL")
class DAG(dag.DAG):
    FIND_SOURCE_FILES: "datalabs.etl.cpt.vignettes.extract.InputFilesListExtractorTask"
    EXTRACT_VIGNETTES_FILE: "datalabs.etl.sftp.extract.SFTPFileExtractorTask"
    CREATE_VIGNETTES_MAPPINGS: "datalabs.etl.cpt.vignettes.transform.VignettesTransformerTask"
    LOAD_VIGNETTES_MAPPINGS: "datalabs.etl.cpt.vignettes.load.DynamoDBLoaderTask"


# pylint: disable=pointless-statement
DAG.FIND_SOURCE_FILES >> DAG.EXTRACT_VIGNETTES_FILE >> DAG.CREATE_VIGNETTES_MAPPINGS >> DAG.LOAD_VIGNETTES_MAPPINGS
