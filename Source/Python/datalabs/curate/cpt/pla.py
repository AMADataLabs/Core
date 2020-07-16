"""File Parser for PLA"""
from dataclasses import dataclass, field
import logging
from typing import List

import pandas
import xml.etree.ElementTree as et

from   datalabs.curate.parse import Parser

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@dataclass
class PLAFields:
    pla_id: List = field(default_factory=list)
    pla_code: List = field(default_factory=list)
    long_descriptor: List = field(default_factory=list)
    medium_descriptor: List = field(default_factory=list)
    short_descriptor: List = field(default_factory=list)
    status: List = field(default_factory=list)
    effective_date: List = field(default_factory=list)
    lab: List = field(default_factory=list)
    manufacturer: List = field(default_factory=list)
    published_date: List = field(default_factory=list)
    test: List = field(default_factory=list)


class PLAParser(Parser):
    ATTRIBUTES = [
        'cdId',
        'cdCode',
    ]
    ELEMENTS = [
        'cdDesc',
        'cdMDesc',
        'cdSDesc',
        'cdStatus',
        'effectiveDate',
        'labName',
        'manufacturerName',
        'publishDate',
        'testName'
    ]
    COLUMNS=[
        'pla_id',
        'pla_code',
        'long_descriptor',
        'medium_descriptor',
        'short_descriptor',
        'status',
        'effective_date',
        'lab',
        'manufacturer',
        'published_date',
        'test'
    ]
    def parse(self, text: str) -> pandas.DataFrame:
        fields = self._extract_fields(text)

        return self._generate_dataframe(fields)

    @classmethod
    def _extract_fields(cls, text):
        fields = PLAFields()
        text_split = text.split("\n", 1)[1]
        root = et.fromstring(text_split)

        for c in root.findall('plaCode'):
            for attribute, column in zip(cls.ATTRIBUTES, cls.COLUMNS[:2]):
                getattr(fields, column).append(c.attrib.get(attribute))

            for element, column in zip(cls.ELEMENTS, cls.COLUMNS[2:]):
                getattr(fields, column).append(c.find(element).text)

        return fields

    @classmethod
    def _generate_dataframe(cls, fields: PLAFields):
        data = list(zip(*[getattr(fields, column) for column in cls.COLUMNS]))

        return pandas.DataFrame(data, columns=cls.COLUMNS)
