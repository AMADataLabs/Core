"""Clinical Descriptor Table module"""
import io
import logging
import re

import pandas

from datalabs.curate.parse import Parser

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class DescriptorParser(Parser):
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


class HeaderedDescriptorParser(DescriptorParser):
    def parse(self, text):
        headerless_text = self._remove_header(text)
        LOGGER.debug('Headerless Text: %s', headerless_text)

        return super().parse(' '.join(self._column_names) + '\n' + headerless_text)

    @classmethod
    def _remove_header(cls, text):
        lines = text.splitlines()

        reversed_lines = lines[::-1]

        return '\r\n'.join(reversed_lines[:reversed_lines.index('')][::-1])


class FixedWidthDescriptorParser(HeaderedDescriptorParser):
    def __init__(self, column_names, descriptor_width):
        super().__init__(column_names)

        self._descriptor_width = descriptor_width

    def parse(self, text):
        headerless_text = self._remove_header(text)

        return pandas.read_fwf(
            io.StringIO(headerless_text),
            names=self._column_names, colspecs=[(0, 5), (6, self._descriptor_width+6)],
            dtype=str
        )

# clinicianDescriptor_file = cliniciandescriptor_obj['Body'].read()
# stream = io.BytesIO(clinicianDescriptor_file)


class LongDescriptorParser(HeaderedDescriptorParser):
    def __init__(self):
        super().__init__(['cpt_code', 'long_descriptor'])


class MediumDescriptorParser(FixedWidthDescriptorParser):
    def __init__(self):
        super().__init__(['cpt_code', 'medium_descriptor'], descriptor_width=48)


class ShortDescriptorParser(FixedWidthDescriptorParser):
    def __init__(self):
        super().__init__(['cpt_code', 'short_descriptor'], descriptor_width=28)


class ClinicianDescriptorParser(DescriptorParser):
    def __init__(self):
        super().__init__(['concept_id', 'cpt_code', 'clinician_descriptor_id', 'clinician_descriptor'])


class ConsumerDescriptorParser(DescriptorParser):
    def __init__(self):
        super().__init__(['concept_id', 'cpt_code', 'consumer_descriptor'])
