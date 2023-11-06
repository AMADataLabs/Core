''' Marketing Aggregator DAG definition. '''
from   datalabs.etl.dag import dag

from   datalabs.etl.marketing.aggregate.extract import EmailValidationExtractorTask
from   datalabs.etl.marketing.aggregate.load import EmailValidationRequestLoaderTask
from   datalabs.etl.marketing.aggregate.poll import AtDataStatusPollingTask


@dag.register(name='PAUSED_DAG')
class DAG(dag.DAG):
    LOAD_EMAILS_VALIDATION: EmailValidationRequestLoaderTask
    POLL_FOR_VALIDATION: AtDataStatusPollingTask
    EXTRACT_EMAILS_VALIDATION: EmailValidationExtractorTask

# pylint: disable=pointless-statement
DAG.LOAD_EMAILS_VALIDATION >> DAG.POLL_FOR_VALIDATION >> DAG.EXTRACT_EMAILS_VALIDATION
