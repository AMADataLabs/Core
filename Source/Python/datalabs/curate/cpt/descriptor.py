"""Clinical Descriptor Table module"""
import io
import logging

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
            io.BytesIO(text),
            names=self._column_names,
            sep=self._separator,
            header=0,
            dtype=str
        )


class HeaderedDescriptorParser(DescriptorParser):
    def parse(self, text):
        headerless_text = self._remove_header(text)
        LOGGER.debug('Headerless Text: %s', headerless_text)

        headered_text = ' '.join(self._column_names) + '\n' + headerless_text

        return super().parse(headered_text.encode())

    @classmethod
    def _remove_header(cls, text):
        decoded_text = None

        try:
            decoded_text = text.decode()
        except UnicodeDecodeError:
            decoded_text = text.decode('cp1252', errors='backslashreplace')

        lines = decoded_text.splitlines()

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


# pylint: disable=invalid-name
class TabDelimitedToFixedWidthDescriptorParser:
    def __init__(self, separator=None):
        self._separator = separator

        if self._separator is None:
            self._separator = '\t'

    def parse(self, text, left_width, right_width):
        headerless_text = self._remove_header(text)[0]
        LOGGER.debug('Headerless Text: %s', headerless_text)

        listStr = headerless_text.split('\r\n')
        txt = ''
        for s in listStr:
            splitStr = s.split('\\t')
            left = left_width.format(splitStr[0])
            right = right_width.format(splitStr[1])
            txt = txt + left + ' ' + right + '\r\n'

        header = self._remove_header(text)[1]
        headered_text = header + '\r\n' + txt

        return self._parse(headered_text.encode())

    def _parse(self, text: str) -> pandas.DataFrame:
        return pandas.read_csv(
            io.BytesIO(text),
            sep=self._separator,
            header=None,
            dtype=str,
            skip_blank_lines=False,
            index_col=False
        )

    @classmethod
    def _remove_header(cls, text):
        decoded_text = None
        try:

            decoded_text = text.decode()
        except UnicodeDecodeError:
            decoded_text = text.decode('cp1252', errors='backslashreplace')

        lines = decoded_text.splitlines()
        reversed_lines = lines[::-1]
        headerless_txt = '\r\n'.join(reversed_lines[:reversed_lines.index('')][::-1])
        descriptor = '\r\n'.join(reversed_lines[reversed_lines.index(''):][::-1])
        return [headerless_txt,descriptor]


class LongFixedWidthDescriptorParser(TabDelimitedToFixedWidthDescriptorParser):
    def parse(self, text, left_width='', right_width=''):
        left_width = "{:<8}"
        right_width = "{:<71}"

        return super().parse(text, left_width, right_width)


class MediumFixedWidthDescriptorParser(TabDelimitedToFixedWidthDescriptorParser):
    def parse(self, text, left_width='', right_width=''):
        left_width = "{:<5}"
        right_width = "{:<48}"

        return super().parse(text, left_width, right_width)


class ShortFixedWidthDescriptorParser(TabDelimitedToFixedWidthDescriptorParser):
    def parse(self, text, left_width='', right_width=''):
        left_width = "{:<5}"
        right_width = "{:<28}"

        return super().parse(text, left_width, right_width)
