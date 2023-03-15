''' Marketing Aggregator DAG definition. '''
from   datalabs.etl.dag import dag
from   datalabs.etl.orm.load import ORMLoaderTask
from   datalabs.etl.s3.extract import S3FileExtractorTask
from   datalabs.etl.sql.extract import SQLExtractorTask


@dag.register(name='MARKETING_AGGREGATOR')
class DAG(dag.DAG):
    EXTRACT_VALIDATED_EMAILS: SQLExtractorTask
    SELECT_VALID_EXISTING_EMAILS: 'datalabs.etl.marketing.aggregate.transform.EmailValidatorTask'
    EXTRACT_EXISTING_EMAILS: SQLExtractorTask
    EXTRACT_INPUTS: S3FileExtractorTask
    CLEAN_INPUTS: 'datalabs.etl.marketing.aggregate.transform.InputDataCleanerTask'
    IDENTIFY_INPUT_EMAILS: 'datalabs.etl.marketing.aggregate.transform.UniqueEmailsIdentifierTask'
    EXTRACT_CURRENT_LISTKEYS: SQLExtractorTask
    IDENTIFY_NEW_EMAILS: 'datalabs.etl.marketing.aggregate.transform.NewEmailsIdentifierTask'
    SELECT_VALID_NEW_EMAILS: 'datalabs.etl.marketing.aggregate.transform.EmailValidatorTask'
    MERGE_INPUTS: 'datalabs.etl.marketing.aggregate.transform.FlatFileGeneratorTask'
    PRUNE_CURRENT_LISTKEYS: 'datalabs.etl.marketing.aggregate.transform.FlatFileGeneratorTask'
    EXTRACT_CONTACT_IDS: SQLExtractorTask
    GENERATE_NEW_CONTACTS: 'datalabs.etl.marketing.aggregate.transform.FlatFileGeneratorTask'
    APPEND_NEW_CONTACTS: ORMLoaderTask
    GENERATE_UPDATED_LISTKEYS: 'datalabs.etl.marketing.aggregate.transform.ListKeysCompilerTask'
    UPDATE_LISTKEYS: ORMLoaderTask
    #UPDATE_SFMC: 'datalabs.etl.marketing.aggregate.transform.SFMCLoaderTask'
    GENERATE_FLAT_FILE: SQLExtractorTask
    LOAD_FLAT_FILE: 'datalabs.etl.marketing.aggregate.transform.SFTPLoaderTask'


# pylint: disable=pointless-statement
DAG.EXTRACT_VALIDATED_EMAILS \
        >> DAG.SELECT_VALID_EXISTING_EMAILS
DAG.EXTRACT_EXISTING_EMAILS \
        >> DAG.SELECT_VALID_EXISTING_EMAILS
DAG.EXTRACT_EXISTING_EMAILS \
        >> DAG.IDENTIFY_NEW_EMAILS
DAG.SELECT_VALID_EXISTING_EMAILS \
        >> DAG.GENERATE_UPDATED_LISTKEYS
DAG.SELECT_VALID_EXISTING_EMAILS \
        >> DAG.PRUNE_CURRENT_LISTKEYS \
        >> DAG.GENERATE_UPDATED_LISTKEYS
DAG.GENERATE_UPDATED_LISTKEYS \
        >> DAG.UPDATE_LISTKEYS
DAG.IDENTIFY_NEW_EMAILS \
        >> DAG.SELECT_VALID_NEW_EMAILS \
        >> DAG.GENERATE_NEW_CONTACTS
DAG.EXTRACT_INPUTS \
        >> DAG.CLEAN_INPUTS
DAG.CLEAN_INPUTS \
        >> DAG.IDENTIFY_INPUT_EMAILS
DAG.CLEAN_INPUTS \
        >> DAG.PRUNE_CURRENT_LISTKEYS \
        >> DAG.GENERATE_UPDATED_LISTKEYS
DAG.IDENTIFY_INPUT_EMAILS \
        >> DAG.IDENTIFY_NEW_EMAILS
DAG.IDENTIFY_INPUT_EMAILS \
        >> DAG.MERGE_INPUTS
DAG.MERGE_INPUTS \
        >> DAG.GENERATE_UPDATED_LISTKEYS
DAG.EXTRACT_CURRENT_LISTKEYS \
        >> DAG.PRUNE_CURRENT_LISTKEYS
DAG.PRUNE_CURRENT_LISTKEYS \
        >> DAG.GENERATE_UPDATED_LISTKEYS
DAG.EXTRACT_CONTACT_IDS \
        >> DAG.GENERATE_NEW_CONTACTS
DAG.GENERATE_NEW_CONTACTS \
        >> DAG.APPEND_NEW_CONTACTS
#DAG.APPEND_NEW_CONTACTS \
#        >> DAG.UPDATE_SFMC
DAG.APPEND_NEW_CONTACTS \
        >> DAG.GENERATE_FLAT_FILE \
        >> DAG.LOAD_FLAT_FILE
#DAG.UPDATE_LISTKEYS \
#        >>DAG.UPDATE_SFMC
DAG.UPDATE_LISTKEYS \
        >> DAG.GENERATE_FLAT_FILE \
        >> DAG.LOAD_FLAT_FILE
