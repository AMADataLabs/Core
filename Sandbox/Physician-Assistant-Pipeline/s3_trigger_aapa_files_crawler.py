import json
import logging
import os
import boto3

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

GLUE_CLIENT = boto3.client('glue')

def lambda_handler(event, context):
    """ trigger the glue crawler that creates a data catalog from state physician assistant license files """

    crawler_name = 'PhysicianAssistantDataCrawler'

    crawler_state = start_glue_crawler_if_ready(crawler_name)

    return crawler_state


def start_glue_crawler_if_ready(crawler_name):
    crawler_state = get_glue_crawler_state(crawler_name)

    if crawler_state == 'READY':
        start_glue_crawler(crawler_name)
    else:
        notify_crawler_not_ready(crawler_name, crawler_state)

    return crawler_state


def get_glue_crawler_state(crawler_name):
    crawler_metadata = GLUE_CLIENT.get_crawler(Name=crawler_name)

    return crawler_metadata.get('Crawler').get('State')


def start_glue_crawler(crawler_name):
    LOGGER.info(f'Crawler {crawler_name} is ready, so we are starting it...')

    response = GLUE_CLIENT.start_crawler(Name=crawler_name)

    LOGGER.debug(f'Crawler {crawler_name} start response: {response}')


def notify_crawler_not_ready(crawler_name, crawler_state):
    LOGGER.info(
        f'Crawler {crawler_name} is in state {crawler_state}. '
        'Only start a crawler when in state READY'
    )