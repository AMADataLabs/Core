""" Generic interface to the API."""
from   abc import ABC, abstractmethod

import io
import pandas as pd
import requests


class AtData(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def _check_processing(self, project_no: str):
        pass


class AtDataAPI(AtData):
    def __init__(self, files, api_endpoint):
        super().__init__()
        self._files = files
        self._api_endpoint = api_endpoint

    def run(self):
        content = requests.post(self._api_endpoint, files=self._files)

        data = self._check_processing(content.json()['project'])

        return data

    # pylint: disable=consider-using-f-string, no-self-use, line-too-long
    def _check_processing(self, project_no):
        status ='Processing'

        while status == 'Processing':
            url = "https://portal.freshaddress.com/REST/ProjectStatus?account=AB254_16345&apikey=D02502F2-382A-4F8D-983E-3B3B82ABFD5B&project={}".format(project_no)

            result_url =requests.get(url)
            result_url.json()
            status = result_url.json()['status']

            if status == 'Returned':
                file_name = result_url.json()['files'][0]
                output = self._get_output(project_no, file_name)

                return output

    # pylint: disable=consider-using-f-string, no-self-use, line-too-long
    def _get_output(self, project_no, file):
        result_url = "https://portal.freshaddress.com/REST/GetFile?account=AB254_16345&apikey=D02502F2-382A-4F8D-983E-3B3B82ABFD5B&project={}&file={}".format(project_no,file)
        result =requests.get(result_url)

        return pd.read_csv(io.StringIO(result.text), sep = '\t')
