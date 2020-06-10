import logging
import pandas
import xml.etree.ElementTree as et

from datalabs.curate.parse import Parser

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class PLAParser(Parser):
    def __init__(self):
        self._pla_code = []
        self._long_description = []
        self._medium_description = []
        self._short_description = []
        self._code_status = []
        self._effective_date = []
        self._lab_name = []
        self._manufacturer_name = []
        self._published_date = []
        self._test_name = []

    def parse(self, text: str) -> pandas.DataFrame:
        self._extract_fields(text)
        return self._generate_dataframe()

    def _extract_fields(self, text):
        root = et.fromstring(text)

        for c in root.findall('plaCode'):
            self._pla_code.append(c.attrib.get('cdCode'))
            self._long_description.append(c.find('cdDesc').text)
            self._medium_description.append(c.find('cdMDesc').text)
            self._short_description.append(c.find('cdSDesc').text)
            self._code_status.append(c.find('cdStatus').text)
            self._effective_date.append(c.find('effectiveDate').text)
            self._lab_name.append(c.find('labName').text)
            self._manufacturer_name.append(c.find('manufacturerName').text)
            self._published_date.append(c.find('publishDate').text)
            self._test_name.append(c.find('testName').text)

    def _generate_dataframe(self):
        df = pandas.DataFrame(list(zip(self._pla_code, self._long_description, self._medium_description,
                                       self._short_description, self._code_status, self._effective_date, self._lab_name,
                                       self._manufacturer_name, self._published_date,self._test_name)),

                              columns=['pla_code', 'long_descriptor', 'medium_descriptor', 'short_descriptor',
                                       'status', 'effective_date', 'lab', 'manufacturer',
                                       'published_date', 'test'])
        return df
