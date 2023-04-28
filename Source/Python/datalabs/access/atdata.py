""" Generic interface to the API."""
import io
import pandas as pd
import requests


# pylint: disable=consider-using-with, line-too-long
class AtData:
    def __init__(self, host, account, api_key):
        self._host = host
        self._account = account
        self._api_key = api_key

    def validate_emails(self, emails: list) -> dict:
        endpoint = 'SendFile'

        _api_endpoint = self._generate_endpoint_url(endpoint)
        ids = list(range(0, len(emails)))
        emails_dict = {'ID':ids,'BEST_EMAIL': emails}
        email_data = pd.DataFrame.from_dict(emails_dict)

        email_data.to_csv('./existing_emails.txt', index=None, sep='\t', mode='a')

        _files = {'file': open('./existing_emails.txt', 'rb')}

        content = requests.post(_api_endpoint, files=_files)

        validation = self._check_processing(content.json()['project'])

        return validation

    # pylint: disable=consider-using-f-string, no-self-use, line-too-long
    def _check_processing(self, project):
        status ='Processing'
        endpoint = 'ProjectStatus'
        url = self._generate_endpoint_url(endpoint) + f"&project={project}"

        while status == 'Processing':
            result_url = requests.get(url)
            status = result_url.json()['status']

            if status == 'Returned':
                file_name = result_url.json()['files'][0]
                output = self._get_output(project, file_name)

                return output

    # pylint: disable=consider-using-f-string, no-self-use, line-too-long
    def _get_output(self, project, file):
        endpoint = 'GetFile'
        result_url = self._generate_endpoint_url(endpoint) + f"&project={project}&file={file}"
        result = requests.get(result_url)

        return pd.read_csv(io.StringIO(result.text), sep = '\t')

    def _generate_endpoint_url(self, endpoint):
        return f"https://{self._host}/REST/{endpoint}?account={self._account}&apikey={self._api_key}"
