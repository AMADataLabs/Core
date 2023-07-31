''' Marketing Aggregator DAG definition. '''
from   datalabs.etl.dag import dag

from   datalabs.etl.marketing.aggregate.transform import EmailValidatorTask
from   datalabs.etl.marketing.aggregate.transform import FlatfileUpdaterTask
from   datalabs.etl.marketing.aggregate.transform import InputDataCleanerTask
from   datalabs.etl.marketing.aggregate.transform import InputsMergerTask
from   datalabs.etl.marketing.aggregate.transform import SFMCPrunerTask
from   datalabs.etl.orm.load import ORMLoaderTask

from   datalabs.etl.s3.extract import S3FileExtractorTask
from   datalabs.etl.sftp.load import SFTPFileLoaderTask
from   datalabs.etl.sql.extract import SQLExtractorTask


@dag.register(name='MARKETING_AGGREGATOR')
class DAG(dag.DAG):
    EXTRACT_FLATFILE: S3FileExtractorTask
    EXTRACT_INPUTS: S3FileExtractorTask
    EXTRACT_CONTACTS: SQLExtractorTask
    CLEAN_INPUTS: InputDataCleanerTask
    VALIDATE_EXISTING_EMAILS: EmailValidatorTask
    MERGE_INPUTS: InputsMergerTask
    VALIDATE_NEW_EMAILS: EmailValidatorTask
    UPDATE_FLATFILE: FlatfileUpdaterTask
    PRUNE_SFMC_ITEMS: SFMCPrunerTask
    LOAD_FLATFILE: SFTPFileLoaderTask
    UPDATE_CONTACT_TABLE: ORMLoaderTask

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
