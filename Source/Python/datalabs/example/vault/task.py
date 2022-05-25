""" Example Lambda function to use with Vault's identity broker for database access.

    Assumes the existance of a schema "vault" with table "hello_world". The table has two string columns:
        | name | honorific |
"""
import os

from   datalabs.task import Task
from   datalabs.access.orm import Database


class CRUDTask(Task):
    TABLE = "vault.hello_world"

    def run(self):
        with self._get_database() as database:
            self._create(database)

            self._read(database)

            self._update(database)

            self._delete(database)

    @classmethod
    def _get_database(cls):
        return Database.from_parameters(
            dict(
                host=os.environ.get("DATABASE_HOST"),
                port=os.environ.get("DATABASE_PORT"),
                backend=os.environ.get("DATABASE_BACKEND"),
                name=os.environ.get("DATABASE_NAME"),
                username=os.environ.get("DATABASE_USERNAME"),
                password=os.environ.get("DATABASE_PASSWORD")
            )
        )

    @classmethod
    def _create(cls, database):
        database.execute(f"INSERT INTO {cls.TABLE} (name, honorific) VALUES ('Janice', 'Doctor')")
        database.execute(f"INSERT INTO {cls.TABLE} (name, honorific) VALUES ('John', 'Sir')")
        database.execute(f"INSERT INTO {cls.TABLE} (name, honorific) VALUES ('Jennifer', 'Madame')")
        database.commit()  # pylint: disable=no-member

    @classmethod
    def _read(cls, database):
        database.execute(f"SELECT honorific FROM {cls.TABLE} WHERE name='Janice'")

    @classmethod
    def _update(cls, database):
        database.execute(f"UPDATE {cls.TABLE} SET honorific="Professor" WHERE name='Jennifer'")
        database.commit()  # pylint: disable=no-member

    @classmethod
    def _delete(cls, database):
        database.execute(f"TRUNCATE {cls.TABLE}")
        database.commit()  # pylint: disable=no-member
