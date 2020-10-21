"Change column names obtained from database"

import pandas


class UpdateColumns:
    @classmethod
    def change_names(cls, dataframe: pandas.DataFrame, names, columns) -> pandas.DataFrame:
        updated_df = dataframe[names].rename(
            columns=columns
        )

        return updated_df
