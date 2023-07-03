''' Marketing Aggregator DAG definition. '''
from   datalabs.etl.dag import dag, JavaTask


@dag.register(name='MARKETING_AGGREGATOR')
class DAG(dag.DAG):
    EXTRACT_ADVANTAGE: JavaTask("datalabs.etl.sql.SqlExtractorTask")
    EXTRACT_ORG_MANAGER: JavaTask("datalabs.etl.sql.SqlExtractorTask")
    EXTRACT_FLATFILE: "datalabs.etl.s3.extract.S3FileExtractorTask"
    EXTRACT_INPUTS: "datalabs.etl.s3.extract.S3FileExtractorTask"
    EXTRACT_CONTACTS: "datalabs.etl.sql.extract.SQLExtractorTask"
    CLEAN_INPUTS: 'datalabs.etl.marketing.aggregate.transform.InputDataCleanerTask'
    VALIDATE_EXISTING_EMAILS: "datalabs.etl.marketing.aggregate.transform.EmailValidatorTask"
    MERGE_INPUTS: "datalabs.etl.marketing.aggregate.transform.InputsMergerTask"
    VALIDATE_NEW_EMAILS: "datalabs.etl.marketing.aggregate.transform.EmailValidatorTask"
    UPDATE_FLATFILE: "datalabs.etl.marketing.aggregate.transform.FlatfileUpdaterTask"
    PRUNE_SFMC_ITEMS: "datalabs.etl.marketing.aggregate.transform.SFMCPrunerTask"
    LOAD_FLATFILE: "datalabs.etl.sftp.load.SFTPFileLoaderTask"
    UPDATE_CONTACT_TABLE: "datalabs.etl.orm.load.ORMLoaderTask"

# pylint: disable=pointless-statement
DAG.EXTRACT_FLATFILE >> DAG.CLEAN_INPUTS
DAG.EXTRACT_INPUTS >> DAG.CLEAN_INPUTS

DAG.EXTRACT_CONTACTS >> DAG.VALIDATE_EXISTING_EMAILS
DAG.EXTRACT_CONTACTS >> DAG.UPDATE_FLATFILE

DAG.CLEAN_INPUTS >> DAG.VALIDATE_EXISTING_EMAILS
DAG.CLEAN_INPUTS >> DAG.MERGE_INPUTS

DAG.VALIDATE_EXISTING_EMAILS >> DAG.UPDATE_FLATFILE
DAG.VALIDATE_EXISTING_EMAILS >> DAG.VALIDATE_NEW_EMAILS

DAG.MERGE_INPUTS >> DAG.VALIDATE_NEW_EMAILS

DAG.VALIDATE_NEW_EMAILS >> DAG.UPDATE_FLATFILE

DAG.UPDATE_FLATFILE >> DAG.LOAD_FLATFILE
DAG.UPDATE_FLATFILE >> DAG.PRUNE_SFMC_ITEMS >> DAG.UPDATE_CONTACT_TABLE
