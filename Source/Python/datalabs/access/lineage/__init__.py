"""Lineage initializing"""
from datalabs.access.lineage.base import \
    LineageException, \
    LineageLogger, \
    register_logger, \
    get_logger
from datalabs.access.lineage.neptune import NeptuneLineageLogger

register_logger('Neptune', NeptuneLineageLogger)
