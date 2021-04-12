""" Database object for AMA's Enterprise Data Warehouse """
from   enum import Enum
import inspect
import logging

import pandas

from   datalabs.access.odbc import ODBCDatabase
import datalabs.curate.dataframe  # pylint: disable=unused-import

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class PartyKeyType(Enum):
    LICENSE = 17
    ME = 18
    SCHOOL = 23
    NPI = 38


class EDW(ODBCDatabase):
    def get_me_numbers(self, chunk_size=None):
        return self.get_party_keys_by_type(PartyKeyType.ME, chunk_size)

    def get_school_ids(self, chunk_size=None):
        return self.get_party_keys_by_type(PartyKeyType.SCHOOL, chunk_size)

    def get_party_keys_by_type(self, party_key_type: PartyKeyType, order_by=None, chunk_size=None):
        data = self.read_in_chunks(
            f"SELECT PARTY_ID, KEY_VAL "
            f"FROM AMAEDW.PARTY_KEY "
            f"WHERE KEY_TYPE_ID={party_key_type.value}",
            order_by=order_by,
            chunk_size=chunk_size,
            caller=inspect.stack()[0][3]
        )

        return data.datalabs.strip()

    def get_me_npi_map(self, order_by=None, chunk_size=None):
        data = self.read_in_chunks(
            f"SELECT K1.KEY_VAL AS ME,K2.KEY_VAL AS NPI_NBR,K1.PARTY_ID "
            f"FROM AMAEDW.PARTY_KEY K1, AMAEDW.PARTY_KEY K2 "
            f"WHERE K1.KEY_TYPE_ID={PartyKeyType.ME.value} AND K1.ACTIVE_IND='Y' AND K1.PARTY_ID=K2.PARTY_ID AND "
            f"K2.KEY_TYPE_ID={PartyKeyType.NPI.value} AND K2.ACTIVE_IND='Y'",
            order_by=order_by,
            chunk_size=chunk_size,
            caller=inspect.stack()[0][3]
        )

        return data.datalabs.strip()

    def get_active_medical_school_map(self, order_by=None, chunk_size=None):
        data = self.read_in_chunks(
            "SELECT PARTY_ID, ORG_NM as MEDSCHOOL_NAME "
            "FROM AMAEDW.ORG_NM "
            "WHERE THRU_DT IS NULL",
            order_by=order_by,
            chunk_size=chunk_size,
            caller=inspect.stack()[0][3]
        )

        return data.datalabs.strip()

    def get_postal_address_map(self, order_by=None, chunk_size=None):
        data = self.read_in_chunks(
            "SELECT POST_CD_ID, SRC_POST_KEY, ADDR_1, ADDR_2, CITY, SRC_STATE_CD, POST_CD, POST_CD_PLUS_4 "
            "FROM AMAEDW.POST_CD P, AMAEDW.STATE S "
            "WHERE P.STATE_ID=S.STATE_ID",
            order_by=order_by,
            chunk_size=chunk_size,
            caller=inspect.stack()[0][3]
        )

        return data.datalabs.strip()

    def read_in_chunks(self, sql, order_by, caller, chunk_size=None):
        chunks = []
        chunk = pandas.DataFrame([True])
        offset = 1
        if not chunk_size:
            chunk_size = 100000

        while not chunk.empty:
            LOGGER.debug('Query %s chunk at offset: %s', caller, offset)
            chunk = self.read(
                sql +
                (' ' if order_by is None else f" ORDER BY {order_by} ") +
                f"LIMIT {chunk_size} OFFSET {offset} ")

            if not chunk.empty:
                chunks.append(chunk)
                offset += chunk_size

        return pandas.concat(chunks, ignore_index=True)
