""" Database object for AIMS """
import inspect
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

    def get_me_entity_map(self, order_by=None, chunk_size=None):
        chunks = self.read_in_chunks(
            f"SELECT key_type_val as me, entity_id "
            f"FROM entity_key_et WHERE key_type='ME' ",
            order_by=order_by,
            chunk_size=chunk_size,
            caller=inspect.stack()[0][3]
        )
        data = pandas.concat(chunks, ignore_index=True)

        return data.datalabs.strip()

    def get_no_contacts(self, order_by=None, chunk_size=None):
        chunks = self.read_in_chunks(
            f"SELECT * "
            f"FROM entity_cat_ct "
            f"WHERE "
            f"(end_dt is null AND category_code = 'NO_CONTACT') or "
            f"(end_dt is null and category_code = 'NO-EMAIL') or "
            f"(end_dt is null and category_code = 'NO-RELEASE')",
            order_by=order_by,
            chunk_size=chunk_size,
            caller=inspect.stack()[0][3]
        )
        data = pandas.concat(chunks, ignore_index=True)

        return data.datalabs.strip()

    def get_pe_descriptions(self, order_by=None, chunk_size=None):
        chunks = self.read_in_chunks(
            f"SELECT present_emp_cd, description "
            f"FROM present_emp_pr",
            order_by=order_by,
            chunk_size=chunk_size,
            caller=inspect.stack()[0][3]
        )
        data = pandas.concat(chunks, ignore_index=True)

        return data.datalabs.strip()

    def get_active_licenses(self, order_by=None, chunk_size=None):
        chunks = self.read_in_chunks(
            f"SELECT entity_id, state_cd, lic_nbr, lic_issue_dt, lic_sts, lic_exp_dt, lic_type, degree_cd, comm_id "
            f"FROM license_lt "
            f"WHERE lic_sts = 'A'",
            order_by=order_by,
            chunk_size=chunk_size,
            caller=inspect.stack()[0][3]
        )
        data = pandas.concat(chunks, ignore_index=True)

        return data.datalabs.strip()

    def get_specialty_descriptions(self, order_by=None, chunk_size=None):
        chunks = self.read_in_chunks(
            f"SELECT spec_cd, description "
            f"FROM spec_pr",
            order_by=order_by,
            chunk_size=chunk_size,
            caller=inspect.stack()[0][3]
        )
        data = pandas.concat(chunks, ignore_index=True)

        return data.datalabs.strip()

    def get_entity_comm_phones(self, order_by=None, chunk_size=None):
        chunks = self.read_in_chunks(
            f"SELECT e.*, p.area_cd||p.exchange||p.phone_nbr as aims_phone "
            f"FROM entity_comm_at e join phone_at p on e.comm_id = p.comm_id "
            f"WHERE comm_cat = 'P'",
            order_by=order_by,
            chunk_size=chunk_size,
            caller=inspect.stack()[0][3]
        )
        data = pandas.concat(chunks, ignore_index=True)

        return data.datalabs.strip()

    def read_in_chunks(self, sql, order_by, chunk_size=None, caller=None):
        chunks = []
        chunk = pandas.DataFrame([True])
        offset = 0
        if not chunk_size:
            chunk_size = 100000

        while not chunk.empty:
            chunk = self._read_chunk(sql, offset, chunk_size, order_by, caller=caller)

            if not chunk.empty:
                chunks.append(chunk)
                offset += chunk_size

        return chunks

    #pylint: disable=too-many-arguments
    def _read_chunk(self, sql, offset, size, order_by, caller):
        LOGGER.debug('Querying %s chunk at offset: %s', caller, offset)
        chunk_sql = re.sub('SELECT ', f"SELECT SKIP {offset} FIRST {size} ", sql, flags=re.I) \
            + ('' if order_by is None else f" ORDER BY {order_by}")

        return self.read(chunk_sql)
