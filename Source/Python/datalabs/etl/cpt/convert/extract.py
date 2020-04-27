""" Object used to extract test data for the CPT CSV ETL. """
from collections import namedtuple
from enum import Enum
import tempfile

import boto3


FileDescriptor = namedtuple('description', 'name tab_separated')


class FileType(Enum):
    Description = 0
    Modifier = 1
    ClinicianDescriptor = 2
    ConsumerDescriptor = 3
    PLA = 4
