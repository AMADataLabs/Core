""" Common Enum definitions for ETLs. """
import enum


class ExtractorLoaderType(enum.IntEnum):
    File = 0
    S3 = 1
    RDS = 2


class ExtractorType(ExtractorLoaderType):
    pass


class LoaderType(ExtractorLoaderType):
    pass
