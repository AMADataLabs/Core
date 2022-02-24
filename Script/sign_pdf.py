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

import datalabs.tool.pdf as pdf

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--input-pdf',
        help='The path to the PDF document to be signed.')
    ap.add_argument('-o', '--output-pdf',
        help='The path to where the signed PDF should be written.')
    ap.add_argument('-c', '--creds-file',
        help='The path to the PKCS12 signing credentials file.')
    ap.add_argument('-p', '--password',
        help='The password to decrypt the signing key (Default: None).')
    args = vars(ap.parse_args())
    LOGGER.debug('Args: %s', args)

    try:
        pdf.sign(args["input_pdf"], args["output_pdf"], args["creds_file"], args["password"])
    except Exception as exception:
        LOGGER.exception(f"Failed to sign PDF.")
        return_code = 1

    exit(return_code)
