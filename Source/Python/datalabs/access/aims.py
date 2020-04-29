""" Database object for AIMS """
import logging
import re

import pandas

from   datalabs.access.odbc import ODBCDatabase
import datalabs.curate.dataframe  # pylint: disable=unused-import

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class AIMS(ODBCDatabase):
    def get_me_entity_count(self):
        record_count = self.read("SELECT count(key_type_val) FROM entity_key_et WHERE key_type='ME'")

        return int(record_count.iloc[0, 0])

    def get_me_entity_map(self, chunk_size=None):
        chunks = self.read_in_chunks(
            f"SELECT key_type_val as me, entity_id "
            f"FROM entity_key_et WHERE key_type='ME' ",
            'me',
            chunk_size,
        )
        data = pandas.concat(chunks, ignore_index=True)

        return data.datalabs.strip()

    def read_in_chunks(self, sql, order_by, chunk_size=None):
        chunks = []
        chunk = pandas.DataFrame([True])
        offset = 0
        if not chunk_size:
            chunk_size = 100000

        while not chunk.empty:
            chunk = self._read_chunk(sql, offset, chunk_size, order_by)

            if not chunk.empty:
                chunks.append(chunk)
                offset += chunk_size

        return chunks

    def _read_chunk(self, sql, offset, size, order_by):
        LOGGER.debug('Get ME/entity ID map chunk at offset: %s', offset)
        chunk_sql = re.sub('SELECT ', f"SELECT SKIP {offset} FIRST {size} ", sql, flags=re.I) \
                  + f" ORDER BY {order_by}"

        return self.read(chunk_sql)
