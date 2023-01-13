"""Task for DAG status notifications"""
import json
import logging

import requests


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class StatusWebHookNotifier():
    def __init__(self, web_hooks, environment):
        self.web_hooks = web_hooks
        self.environment = environment

    def notify(self, dag, execution_time, status):
        message = {
            'text': f'The {dag} DAG run at {execution_time.replace("T", " ")} UTC in the {self.environment} '
                    f'environment has status {status.value}.'
        }
        LOGGER.info('Message %s', message)
        for web_hook in self.web_hooks:
            LOGGER.info("Test")
            requests.post(web_hook, data=json.dumps(message), headers={'Content-Type': 'application/json'})
        LOGGER.info('Web hook notification sent to %s', self.web_hooks)
