""" Database object for AIMS """
import logging

import pandas

import datalabs.access.database as db
import datalabs.curate.dataframe as df

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class AIMS(db.Database):
    def get_me_entity_count(self):
        record_count = self.read("SELECT count(key_type_val) FROM entity_key_et WHERE key_type='ME'")

        return int(record_count.iloc[0,0])

    def get_me_entity_map(self, chunk_size=100000, order_by='me'):
        chunks = self._get_me_entity_map_chunks(chunk_size, order_by)
        data = pandas.concat(chunks, ignore_index=True)

        return df.strip(data)

    def _get_me_entity_map_chunks(self, chunk_size, order_by):
        chunks = []
        chunk = pandas.DataFrame([True])
        offset = 0

        while not chunk.empty:
            LOGGER.debug(f'Get ME/entity ID map chunk at offset: {offset}')
            chunk = self.read(
                f"SELECT SKIP {offset} FIRST {chunk_size} key_type_val as me, entity_id "
                f"FROM entity_key_et WHERE key_type='ME' "
                f"ORDER BY {order_by}"
            )

            if not chunk.empty:
                chunks.append(chunk)
                offset += chunk_size

        return chunks
