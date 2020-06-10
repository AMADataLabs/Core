import logging
import pandas
import xml.etree.ElementTree as et

from datalabs.curate.parse import Parser

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class PLAParser(Parser):
    def __init__(self):
        self.pla_code = []
        self.long_description = []
        self.medium_description = []
        self.short_description = []
        self.code_status = []
        self.effective_date = []
        self.lab_name = []
        self.manufacturer_name = []
        self.published_date = []
        self.test_name = []

    def parse(self, text: str) -> pandas.DataFrame:
        self._extract_fields(text)
        return self._generate_dataframe()

    def _extract_fields(self, text):
        root = et.fromstring(text)

        for c in root.findall('plaCode'):
            self.pla_code.append(c.attrib.get('cdCode'))
            self.long_description.append(c.find('cdDesc').text)
            self.medium_description.append(c.find('cdMDesc').text)
            self.short_description.append(c.find('cdSDesc').text)
            self.code_status.append(c.find('cdStatus').text)
            self.effective_date.append(c.find('effectiveDate').text)
            self.lab_name.append(c.find('labName').text)
            self.manufacturer_name.append(c.find('manufacturerName').text)
            self.published_date.append(c.find('publishDate').text)
            self.test_name.append(c.find('testName').text)

    def _generate_dataframe(self):
        df = pandas.DataFrame(list(zip(self.pla_code, self.long_description, self.medium_description,
                                       self.short_description, self.code_status, self.effective_date, self.lab_name,
                                       self.manufacturer_name, self.published_date,self.test_name)),

                              columns=['pla_code', 'long_descriptor', 'medium_descriptor', 'short_descriptor',
                                       'status', 'effective_date', 'lab', 'manufacturer',
                                       'published_date', 'test'])
        return df
