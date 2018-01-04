from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from mvc.db import mixins

BASE = declarative_base()


class MVCBase(mixins.TransactionMixin, mixins.DictionaryMixin,
              mixins.TimestampMixin, mixins.SoftDeleteMixin):
    pass


class Person(BASE, MVCBase):
    __tablename__ = 'person'
    id = Column(String(36), primary_key=True)
    name = Column(String(250), nullable=False)


class Address(BASE, MVCBase):
    __tablename__ = 'address'
    id = Column(String(36), primary_key=True)
    address_line = Column(String(250))
    postal_code = Column(String(10), nullable=False)
    person_id = Column(String(36), ForeignKey('person.id'))
    person = relationship(Person, backref='addresses')
