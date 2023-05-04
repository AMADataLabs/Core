""" Generic interface to the API."""
import io
from io import BytesIO
import pandas as pd
import requests


# pylint: disable=consider-using-with, line-too-long
class AtData:
    def __init__(self, host, account, api_key):
        self._host = host
        self._account = account
        self._api_key = api_key

    def validate_emails(self, emails: list) -> dict:
        api_endpoint = self._generate_endpoint_url("SendFile", parameters=dict(project=None, file=None))

        ids = list(range(0, len(emails)))
        emails_dict = {'ID':ids,'BEST_EMAIL': emails}
        email_data = pd.DataFrame.from_dict(emails_dict)

        emails_file = BytesIO()
        emails_file.name = "emails7.txt"
        email_data.to_csv(emails_file, index=None, sep='\t', mode='a')
        emails_file.seek(0)
        content = requests.post(api_endpoint, files={'file':emails_file})
        validation = self._check_processing(content.json()['project'])

        return validation

    # pylint: disable=consider-using-f-string, no-self-use, line-too-long
    def _check_processing(self, project):
        status ='Processing'
        url = self._generate_endpoint_url("ProjectStatus", parameters=dict(project=project, file=None))
        output = None

        while status == 'Processing':
            result_url = requests.get(url)
            status = result_url.json()['status']

            if status == 'Returned':
                file_name = result_url.json()['files'][0]
                output = self._get_output(project, file_name)

        return output

    # pylint: disable=consider-using-f-string, no-self-use, line-too-long
    def _get_output(self, project, file):
        result_url = self._generate_endpoint_url("GetFile", parameters=dict(project=project, file=file))
        result = requests.get(result_url)

        return pd.read_csv(io.StringIO(result.text), sep = '\t')

    def _generate_endpoint_url(self, endpoint, parameters:dict=None):
        project, file = parameters["project"], parameters["file"]
        url = f"https://{self._host}/REST/{endpoint}?account={self._account}&apikey={self._api_key}"

        if project is not None and file is not None:
            url = url + f"&project={project}&file={file}"
        elif project is not None and file is None:
            url = url + f"&project={project}"

        return url
