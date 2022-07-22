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
            'text': 'The {} DAG run at {} UTC in the {} environment has status {}.'.format(
                dag,
                execution_time,
                self.environment,
                status.value
            )
        }
        LOGGER.info('Message %s', message)
        for web_hook in self.web_hooks:
            LOGGER.info("Test")
            requests.post(web_hook, data=json.dumps(message), headers={'Content-Type': 'application/json'})
        LOGGER.info('WEB HOOK NOTIFICATION SENT TO %s', self.web_hooks)
