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
class TabDelimitedToFixedWidthDescriptorFormatter:
    def __init__(self, code_width: int, descriptor_width: int):
        self._code_format = f"{{:<{code_width}}}"
        self._descriptor_format = f"{{:<{descriptor_width}}}"

    def format(self, text):
        header, descriptors = self._parse(text)
        reformatted_descriptors = self._reformat_columns(descriptors)

        return self._reassemble_text(header, reformatted_descriptors)

    def _parse(self, text):
        decoded_text = self._decode(text)
        header, headerless_text = self._remove_header(decoded_text)

        descriptors = pandas.read_csv(
            io.BytesIO(headerless_text.encode()),
            sep=r"\\t",
            names=["code", "descriptor"],
            header=None,
            dtype=str,
            index_col=False
        )

        return header, descriptors

    def _reformat_columns(self, descriptors):
        descriptors.code = descriptors.code.apply(self._code_format.format)
        descriptors.descriptor = descriptors.descriptor.apply(self._descriptor_format.format)

        return descriptors

    @classmethod
    def _reassemble_text(cls, header, descriptors):
        descriptors = descriptors.to_string(header = False, index = False)

        if len(header) != 0:
            headered_text = header + '\r\n' + descriptors
        else:
            headered_text = descriptors

        return pandas.read_csv(
            io.BytesIO(headered_text.encode()),
            sep="\t",
            header=None,
            dtype=str,
            skip_blank_lines=False,
            index_col=False
        )

    @classmethod
    def _remove_header(cls, decoded_text):
        lines = decoded_text.splitlines()
        reversed_lines = lines[::-1]

        try:
            headerless_text = '\r\n'.join(reversed_lines[:reversed_lines.index('')][::-1])
            header = '\r\n'.join(reversed_lines[reversed_lines.index(''):][::-1])
        except ValueError:
            header = ''
            headerless_text = '\r\n'.join(lines)

        return [header, headerless_text]

    @classmethod
    def _decode(cls, text):
        decoded_text = None

        try:
            decoded_text = text.decode()
        except UnicodeDecodeError:
            decoded_text = text.decode('cp1252', errors='backslashreplace')

        return decoded_text

class LongFixedWidthDescriptorFormatter(TabDelimitedToFixedWidthDescriptorFormatter):
    def __init__(self):
        super().__init__(8, 71)


class MediumFixedWidthDescriptorFormatter(TabDelimitedToFixedWidthDescriptorFormatter):
    def __init__(self):
        super().__init__(5, 48)


class ShortFixedWidthDescriptorFormatter(TabDelimitedToFixedWidthDescriptorFormatter):
    def __init__(self):
        super().__init__(5, 28)
