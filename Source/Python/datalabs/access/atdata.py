""" Generic interface to the API."""
from datetime import datetime

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

    def request_email_validation(self, emails: list) -> dict:
        request_id = None

        api_endpoint = self._generate_endpoint_url("SendFile", parameters={})

        email_data = self._create_emails_dataframe(emails)

        emails_file = self._create_payload_file(email_data)

        request_id = self._post_file_to_endpoint(api_endpoint, emails_file)

        return request_id

    def get_validation_status(self, request_id):
        ''' Get the status of the validation, and a list of result files if finished:
            {
                "status": "Processing" | "Returned",
                "files": [] | ["file ID"]
            }
        '''
        file = None
        url = self._generate_endpoint_url("ProjectStatus", parameters=dict(project=request_id))

        response = requests.get(url).json()

        if response['status'] == "Returned":
            file = response['files'][0]

        return (response['status'], file)

    def get_validation_results(self, request_id, file):
        valid_emails, output = None, None
        result_url = self._generate_endpoint_url("GetFile", parameters=dict(project=request_id, file=file))

        response = requests.get(result_url)

        if 'File not found' not in response.text:
            data = pd.read_csv(io.StringIO(response.text), sep = '\t')
            valid_emails = data[data.FINDING != 'W'].drop(columns=column.INVALID_EMAILS_COLUMNS)
            output = list(valid_emails.EMAIL.values)

        return output

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
        ''' Call the AtData API to submit the list of emails to validate, returning the request ID ("project" in the
            response data).
        '''
        response = requests.post(api_endpoint, files={'file':emails_file})

        return response.json()['project']

    def _generate_endpoint_url(self, endpoint, parameters:dict=None):
        url = f"https://{self._host}/REST/{endpoint}?account={self._account}&apikey={self._api_key}"

        url = url + ("".join(f"&{key}={value}" for key, value in parameters.items()))

        return url
