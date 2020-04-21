#!/usr/bin/env python

from   collections import namedtuple
import logging
import os

import pandas as pd

import settings
from   datalabs.curate.polo.entity import EntityTableCleaner

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


Parameters = namedtuple('Parameters', 'input output kwargs')


def main():
    parameter_set = [
        Parameters(
            input='ENTITY_COMM_AT_FILE_RAW',
            output='ENTITY_COMM_AT_FILE',
            kwargs=dict(
                row_filters={'comm_cat': 'A '},
                column_filters={name:'ent_comm_'+name for name in [
                    'entity_id', 'comm_type', 'begin_dt', 'comm_id', 'end_dt', 'src_cat_code'
                ]},
                datestamp_columns=['begin_dt', 'end_dt']
                # types={'entity_id': 'uint32', 'comm_id': 'uint32'},
                # types={'ent_comm_entity_id': 'str', 'ent_comm_comm_id': 'str'},
            )
        ),
        Parameters(
            input='ENTITY_COMM_USG_FILE_RAW',
            output='ENTITY_COMM_USG_FILE',
            kwargs=dict(
                row_filters={'comm_cat': 'A '},
                column_filters={name:name if name.startswith('usg_') else 'usg_'+name for name in [
                    'entity_id', 'comm_type', 'comm_usage', 'usg_begin_dt', 'comm_id', 'comm_type', 'end_dt', 'src_cat_code'
                ]},
                datestamp_columns=['usg_begin_dt', 'end_dt']
                # types={'entity_id': 'uint32', 'comm_id': 'uint32'},
                # types={'usg_entity_id': 'str', 'usg_comm_id': 'str'},
            )

        ),
        Parameters(
            input='POST_ADDR_AT_FILE_RAW',
            output='POST_ADDR_AT_FILE',
            kwargs=dict(
                column_filters={name:'post_'+name for name in [
                    'comm_id', 'addr_line2', 'addr_line1', 'addr_line0', 'city_cd', 'state_cd', 'zip', 'plus4'
                ]},
                # types={'comm_id': 'uint32'}
                # types={'post_comm_id': 'str'}
            )
        ),
        Parameters(
            input='LICENSE_LT_FILE_RAW',
            output='LICENSE_LT_FILE',
            kwargs=dict(
                defaults={'comm_id': '0'},
                datestamp_columns=['lic_exp_dt', 'lic_issue_dt', 'lic_rnw_dt']
                # types={'entity_id': 'uint32', 'comm_id': 'uint32'},
                # types={'entity_id': 'str', 'comm_id': 'str'},
            )
        ),
        Parameters(
            input='ENTITY_KEY_ET_FILE_RAW',
            output='ENTITY_KEY_ET_FILE',
            kwargs=dict(
                # types={'entity_id': 'uint32'}
                # types={'entity_id': 'str'}
            )
        ),
    ]

    for parameters in parameter_set:
        input_file = os.environ.get(parameters.input)
        output_file = os.environ.get(parameters.output)
        LOGGER.info('--------------------------------')
        EntityTableCleaner(input_file, output_file, **parameters.kwargs).clean()


if __name__ == '__main__':
    main()

