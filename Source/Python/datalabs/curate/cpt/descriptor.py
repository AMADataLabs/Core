"""Clinical Descriptor Table module"""
import io
import re

import pandas


class DescriptorParser:
    def __init__(self, column_names, separator=None):
        self._column_names = column_names
        self._separator = separator

        if self._separator is None:
            self._separator = '\t'

    def parse(self, text: str) -> pandas.DataFrame:
        return pandas.read_csv(
            io.StringIO(text),
            names=self._column_names,
            sep=self._separator,
            header=0,
            dtype=str
        )


# clinicianDescriptor_file = cliniciandescriptor_obj['Body'].read()
# stream = io.BytesIO(clinicianDescriptor_file)


class LongDescriptorParser(DescriptorParser):
    def __init__(self):
        super().__init__(['cpt_code', 'long_descriptor'])

    def parse(self, text):
        headerless_text = self._remove_header(text)

        return super().parse('col1\tcol2\n' + headerless_text)

    @classmethod
    def _remove_header(cls, text):
        return re.sub(r'..*\n\n', '', text, flags=re.DOTALL)


class ClinicianDescriptorParser(DescriptorParser):
    def __init__(self):
        super().__init__(['concept_id', 'cpt_code', 'clinician_descriptor_id', 'clinician_descriptor'])


class ConsumerDescriptorParser(DescriptorParser):
    def __init__(self):
        super().__init__(['concept_id', 'cpt_code', 'consumer_descriptor'])
