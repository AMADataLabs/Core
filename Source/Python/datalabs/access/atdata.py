""" Generic interface to the API."""
from datetime import datetime
import time

import io
from io import BytesIO
import pandas as pd
import requests

from   datalabs.etl.marketing.aggregate import column


# pylint: disable=consider-using-with, line-too-long
class AtData:
    def __init__(self, host, account, api_key):
        self._host = host
        self._account = account
        self._api_key = api_key

    def validate_emails(self, emails: list) -> dict:
        api_endpoint = self._generate_endpoint_url("SendFile", parameters={})

        email_data = self._create_emails_dataframe(emails)

        emails_file = self._create_payload_file(email_data)

        content = self._post_file_to_endpoint(api_endpoint, emails_file)

        validation = self._wait_for_validation(content.json()['project'])

        return validation

    def _generate_endpoint_url(self, endpoint, parameters:dict=None):
        url = f"https://{self._host}/REST/{endpoint}?account={self._account}&apikey={self._api_key}"

        url = url + ("".join(f"&{key}={value}" for key, value in parameters.items()))

        return url

    @classmethod
    def _create_emails_dataframe(cls, emails):
        ids = list(range(0, len(emails)))

        return pd.DataFrame(data=dict(ID=ids, EMAIL=emails))

    @classmethod
    def _create_payload_file(cls, email_data):
        emails_file = BytesIO()

        date_time = datetime.now().strftime("%Y%m%d-%H%M%S")

        emails_file.name = f"emails_{date_time}.txt"

        email_data.to_csv(emails_file, index=None, sep='\t', mode='a')

        emails_file.seek(0)

        return emails_file

    @classmethod
    def _post_file_to_endpoint(cls, api_endpoint, emails_file):
        return requests.post(api_endpoint, files={'file':emails_file})

    def _wait_for_validation(self, project):
        status ='Processing'
        results, output = None, None

        url = self._generate_endpoint_url("ProjectStatus", parameters=dict(project=project))

        while status == 'Processing':
            time.sleep(60)

            status, results = self._get_validation_status(url)

        if status == 'Returned':
            output = self._get_output(project, results.json()['files'][0])

        return output

    @classmethod
    def _get_validation_status(cls, url):
        results = requests.get(url)
        status = results.json()['status']

        return (status, results)

    def _get_output(self, project, file):
        result_url = self._generate_endpoint_url("GetFile", parameters=dict(project=project, file=file))
        result = requests.get(result_url)

        data = pd.read_csv(io.StringIO(result.text), sep = '\t')

        valid_emails = data[data.FINDING != 'W'].drop(columns=column.INVALID_EMAILS_COLUMNS)

        return list(valid_emails.EMAIL.values)
