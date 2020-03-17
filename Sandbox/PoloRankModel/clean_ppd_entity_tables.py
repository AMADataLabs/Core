#!/usr/bin/env python

from   collections import namedtuple
import logging
import os

import pandas as pd

import settings
import datalabs.analysis.polo.rank.data.ppd as ppd_data

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


Parameters = namedtuple('Parameters', 'input output cleaner')


def main():
    parameter_set = [
        # Parameters(
        #     input='ENTITY_COMM_AT_FILE_RAW',
        #     output='ENTITY_COMM_AT_FILE',
        #     cleaner=ppd_data.EntityCommAtCleaner
        # ),
        # Parameters(
        #     input='ENTITY_COMM_USG_FILE_RAW',
        #     output='ENTITY_COMM_USG_FILE',
        #     cleaner=ppd_data.EntityCommUsgCleaner
        # ),
        # Parameters(
        #     input='POST_ADDR_AT_FILE_RAW',
        #     output='POST_ADDR_AT_FILE',
        #     cleaner=ppd_data.PostAddrAtCleaner
        # ),
        Parameters(
            input='LICENSE_LT_FILE_RAW',
            output='LICENSE_LT_FILE',
            cleaner=ppd_data.LicenseLtCleaner
        ),
        # Parameters(
        #     input='ENTITY_KEY_ET_FILE_RAW',
        #     output='ENTITY_KEY_ET_FILE',
        #     cleaner=ppd_data.EntityKeyEtCleaner
        # ),
    ]

    for parameters in parameter_set:
        input_file = os.environ.get(parameters.input)
        output_file = os.environ.get(parameters.output)
        LOGGER.info('--------------------------------')
        parameters.cleaner(input_file, output_file).clean()


if __name__ == '__main__':
    main()

