from   datalabs.model.polo.rank.data.entity import EntityTableCleaner

class EntityCommAtCleaner(EntityTableCleaner):
    def __init__(self, input_path, output_path):
        column_names = 'entity_id', 'comm_type', 'begin_dt', 'comm_id', 'end_dt', 'src_cat_code'
        column_filters = {name:'ent_comm_'+name for name in column_names}

        super().__init__(
            input_path,
            output_path,
            row_filters={'comm_cat': 'A '},
            column_filters=column_filters,
            types={'entity_id': 'uint32', 'comm_id': 'uint32'},
            datestamp_columns=['begin_dt', 'end_dt']
        )


class EntityCommUsgCleaner(EntityTableCleaner):
    def __init__(self, input_path, output_path):
        column_names = ['entity_id', 'comm_type', 'comm_usage', 'usg_begin_dt', 'comm_id', 'comm_type',
                        'end_dt', 'src_cat_code']
        column_filters = {name:'usg_'+name for name in column_names}
        column_filters['usg_begin_dt'] == 'usg_begin_dt'

        super().__init__(
            input_path,
            output_path,
            row_filters={'comm_cat': 'A '},
            column_filters=column_filters,
            types={'entity_id': 'uint32', 'comm_id': 'uint32'},
            datestamp_columns=['usg_begin_dt', 'end_dt']
        )


class PostAddrAtCleaner(EntityTableCleaner):
    def __init__(self, input_path, output_path):
        column_names = ['comm_id', 'addr_line2', 'addr_line1', 'addr_line0', 'city_cd',
                        'state_cd', 'zip', 'plus4']
        column_filters = {name:'post_'+name for name in column_names}

        super().__init__(
            input_path,
            output_path,
            column_filters=column_filters,
            types={'comm_id': 'uint32'}
        )


class LicenseLtCleaner(EntityTableCleaner):
    def __init__(self, input_path, output_path):
        super().__init__(
            input_path,
            output_path,
            types={'entity_id': 'uint32', 'comm_id': 'uint32'},
            datestamp_columns=['lic_exp_dt', 'lic_issue_dt', 'lic_rnw_dt']
        )

    def _clean_values(self, table):
        table = super()._clean_values(table)
        table = self._insert_default_comm_id(table)

        return table

    @classmethod
    def _insert_default_comm_id(cls, table):
        table['comm_id'].fillna('0', inplace=True)

        return table


class EntityKeyEtCleaner(EntityTableCleaner):
    def __init__(self, input_path, output_path):
        super().__init__(
            input_path,
            output_path,
            types={'entity_id': 'uint32'}
        )
