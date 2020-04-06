""" Database object for AIMS """
import logging

import pandas

import datalabs.access.database as db

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class AIMS(db.Database):
    def get_me_entity_count(self):
        record_count = self.read("SELECT count(key_type_val) FROM entity_key_et WHERE key_type='ME'")

        return int(record_count.iloc[0,0])

    def get_me_entity_map(self, chunk_size=1000, order_by='me'):
        data = []
        chunk = pandas.DataFrame([True])
        offset = 0

        while not chunk.empty:
            LOGGER.debug(f'Chunk offset: {offset}')
            chunk = self.read(
                f"SELECT SKIP {offset} FIRST {chunk_size} key_type_val as me, entity_id "
                f"FROM entity_key_et WHERE key_type='ME' "
                f"ORDER BY {order_by}"
            )

            if not chunk.empty:
                data.append(chunk)
                offset += chunk_size


        return pandas.concat(data, ignore_index=True)
