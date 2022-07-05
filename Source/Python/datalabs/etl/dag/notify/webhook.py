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
            'Message': 'The {} DAG run at {} UTC in the {} environment has status {}.'.format(
                dag,
                execution_time,
                self.environment,
                status.value
            )
        }
        LOGGER.info('Message %s', message)
        LOGGER.info('web_hook %s', self.web_hooks)
        for web_hook_url in self.web_hooks:
            requests.post(web_hook_url, data=json.dumps(message), headers={'Content-Type': 'application/json'})
        LOGGER.info('WEB HOOK NOTIFICATION SENT TO %s', self.web_hooks)
