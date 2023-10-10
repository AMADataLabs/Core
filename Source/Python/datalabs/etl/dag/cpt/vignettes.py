''' DAG definition for Vignettes-CPT API ETL '''
from   datalabs.etl.dag import dag


@dag.register(name="VIGNETTES_CPT_ETL")
class DAG(dag.DAG):
    EXTRACT_VIGNETTES_FILE: "datalabs.etl.sftp.extract.SFTPFileExtractorTask"
    CREATE_VIGNETTES_MAPPINGS: "datalabs.etl.cpt.vignettes.transform.VignettesTransformerTask"
    LOAD_VIGNETTES_MAPPINGS: "datalabs.etl.cpt.vignettes.load.DynamoDBLoaderTask"


# pylint: disable=expression-not-assigned
DAG.EXTRACT_VIGNETTES_FILE >> DAG.CREATE_VIGNETTES_MAPPINGS >> DAG.LOAD_VIGNETTES_MAPPINGS
