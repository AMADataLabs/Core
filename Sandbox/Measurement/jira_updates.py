import requests
from requests.auth import HTTPBasicAuth
import json
import os
from dataclasses import dataclass
import logging

@dataclass
class JiraProjectParameters:
    token: str
    base_url: str
    email: str
    project_id: str
    project_name: str
    folder: str

class JiraProject:
    def __init__(self, parameters):
        self.parameters = parameters
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        self.base_url = parameters.base_url
        self.token = parameters.token
        self.email = parameters.email
        self.project_id = parameters.project_id
        self.task_id = '10223'
        self.epic_id = '10224'
        self.subtask_id = '10225'
        
        self.auth = HTTPBasicAuth(parameters.email, parameters.token)
        self.tracking_file = f'{parameters.folder}{parameters.project_name}_BOARD_TRACKING.csv'

    def create_issue(self, description, epic_name, summary, label):
        url = self.base_url + 'issue'

        headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
        }

        payload = json.dumps( {
        "fields": {
            "issuetype": {
            "id": self.task_id
            },
            "parent": {
            "id": epic_name
            },
            "labels": [
            label,
            ],

            "project": {
            "id": self.project_id
            },

            "summary": summary,
            'description': description
        },
        "update": {}
        } )

        response = requests.request(
        "POST",
        url,
        data=payload,
        headers=headers,
        auth=self.auth
        )

        results = response.json()
        
        return(results)

    def create_epic(self, epic_title, description):
        url = self.base_url + 'issue'

        headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
        }

        payload = json.dumps( {
        "fields": {
            "issuetype": {
            "id": self.epic_id
            },
            "project": {
            "id": self.project_id
            },

            "summary": epic_title,
            'description': description
        },
        "update": {}
        } )

        response = requests.request(
        "POST",
        url,
        data=payload,
        headers=headers,
        auth=self.auth
        )

        results = response.json()
        return results

    def add_file(self, filename, issue_key):
        
        url = self.base_url + f"issue/{issue_key}/attachments"

        headers = {
            "Accept": "application/json",
            "X-Atlassian-Token": "no-check"
        }

        response = requests.request(
            "POST",
            url,
            headers = headers,
            auth = self.auth,
            files = {
                "file": (filename, open(filename,"rb"), "application-type")
            }
        )
        return response


def create_description(text):
        description = {
        "version": 1,
        "type": "doc",
        "content": [
            {
            "type": "paragraph",
            "content": [
                {
                "type": "text",
                "text": text
                }
            ]
            }
        ]
        }

        return description