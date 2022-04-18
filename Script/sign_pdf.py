from   abc import ABC, abstractmethod
import argparse
import io
import logging
import os
from   pathlib import Path
import re
import shutil
import sys
from   zipfile import ZipFile

from   datalabs.tool.pdf import PDFSigner

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--input-pdf', required=True,
        help='The path to the PDF document to be signed.')
    ap.add_argument('-o', '--output-pdf', required=True,
        help='The path to where the signed PDF should be written.')
    ap.add_argument('-c', '--creds-file', required=True,
        help='The path to the PKCS12 signing credentials file.')
    ap.add_argument('-p', '--password', required=True,
        help='The password to decrypt the signing key.')
    ap.add_argument('-r', '--recipient', required=True,
        help='The recipient of the downloaded PDF.')
    args = vars(ap.parse_args())
    LOGGER.debug('Args: %s', args)

    try:
        PDFSigner.sign(args["input_pdf"], args["output_pdf"], args["creds_file"], args["password"], args["recipient"])
    except Exception as exception:
        LOGGER.exception(f"Failed to sign PDF.")
        return_code = 1

    exit(return_code)
