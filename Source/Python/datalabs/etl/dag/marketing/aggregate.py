''' Marketing Aggregator DAG definition. '''
from   datalabs.etl.dag import dag

from   datalabs.etl.marketing.aggregate.extract import EmailValidationExtractorTask
from   datalabs.etl.marketing.aggregate.load import EmailValidationRequestLoaderTask
from   datalabs.etl.marketing.aggregate.transform import FlatfileUpdaterTask
from   datalabs.etl.marketing.aggregate.transform import InputDataCleanerTask
from   datalabs.etl.marketing.aggregate.transform import InputsMergerTask
from   datalabs.etl.marketing.aggregate.transform import SFMCPrunerTask
from   datalabs.etl.marketing.aggregate.transform import SourceFileListTransformerTask
from   datalabs.etl.orm.load import ORMLoaderTask

from   datalabs.etl.sftp.extract import SFTPDirectoryListingExtractorTask
from   datalabs.etl.sftp.load import SFTPFileLoaderTask
from   datalabs.etl.sql.extract import SQLExtractorTask


@dag.register(name='MARKETING_AGGREGATOR')
class DAG(dag.DAG):
    EXTRACT_INPUT_PATHS: SFTPDirectoryListingExtractorTask
    CREATE_SOURCE_FILE_LISTS: SourceFileListTransformerTask
    EXTRACT_CONTACTS: SQLExtractorTask
    CLEAN_INPUTS: InputDataCleanerTask
    LOAD_EMAILS_VALIDATION: EmailValidationRequestLoaderTask
    EXTRACT_EMAILS_VALIDATION: EmailValidationExtractorTask
    MERGE_INPUTS: InputsMergerTask
    UPDATE_FLATFILE: FlatfileUpdaterTask
    PRUNE_SFMC_ITEMS: SFMCPrunerTask
    LOAD_FLATFILE: SFTPFileLoaderTask
    UPDATE_CONTACT_TABLE: ORMLoaderTask

# pylint: disable=pointless-statement
DAG.EXTRACT_INPUT_PATHS >> DAG.CREATE_SOURCE_FILE_LISTS >> DAG.CLEAN_INPUTS

DAG.EXTRACT_CONTACTS >> DAG.LOAD_EMAILS_VALIDATION >> DAG.EXTRACT_EMAILS_VALIDATION
DAG.EXTRACT_CONTACTS >> DAG.UPDATE_FLATFILE

DAG.CLEAN_INPUTS >> DAG.LOAD_EMAILS_VALIDATION >> DAG.EXTRACT_EMAILS_VALIDATION
DAG.CLEAN_INPUTS >> DAG.MERGE_INPUTS

DAG.EXTRACT_EMAILS_VALIDATION >> DAG.UPDATE_FLATFILE
DAG.EXTRACT_EMAILS_VALIDATION >> DAG.LOAD_EMAILS_VALIDATION >> DAG.EXTRACT_EMAILS_VALIDATION

DAG.MERGE_INPUTS >> DAG.LOAD_EMAILS_VALIDATION >> DAG.EXTRACT_EMAILS_VALIDATION

DAG.EXTRACT_EMAILS_VALIDATION >> DAG.UPDATE_FLATFILE

DAG.UPDATE_FLATFILE >> DAG.LOAD_FLATFILE
DAG.UPDATE_FLATFILE >> DAG.PRUNE_SFMC_ITEMS >> DAG.UPDATE_CONTACT_TABLE
