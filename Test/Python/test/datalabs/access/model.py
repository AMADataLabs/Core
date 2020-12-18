""" SQLAlchemy models for CPT """
import sqlalchemy as sa
from   sqlalchemy.ext.declarative import declarative_base

from   datalabs.sqlalchemy import metadata

Base = declarative_base(metadata=metadata())  # pylint: disable=invalid-name


class Foo(Base):
    __tablename__ = 'foo'

    this = sa.Column(sa.String, primary_key=True)
    that = sa.Column(sa.String, nullable=False)

    def __repr__(self):
        return "<Foo(this='{}', that='{}')>".format(self.this, self.that)


class Bar(Base):
    __tablename__ = 'bar'

    one = sa.Column(sa.Integer, primary_key=True)
    two = sa.Column(sa.String, nullable=False)

    def __repr__(self):
        return "<Bar(one={}, two='{}')>".format(self.one, self.two)


class Poof(Base):
    __tablename__ = 'poof'

    a = sa.Column(sa.Integer, primary_key=True)
    b = sa.Column(sa.Boolean, nullable=False)

    def __repr__(self):
        return "<Poof(a={}, b={})>".format(self.a, self.b)
