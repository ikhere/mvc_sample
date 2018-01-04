import six

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import object_mapper


class TransactionMixin(object):
    def _flush(self, session):
        try:
            session.flush()
        except DatabaseError:
            session.rollback()

    def save(self, session):
        with session.begin():
            session.add(self)
            self._flush(session)

    def update(self, values):
        for k, v in six.iteritems(values):
            setattr(self, k, v)

    def delete(self, session):
        with session.begin():
            session.delete(self)
            self._flush(session)


class DictionaryMixin(six.Iterator):
    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __contains__(self, key):
        try:
            getattr(self, key)
        except AttributeError:
            return False
        return True

    def __iter__(self):
        columns = list(dict(object_mapper(self).columns).keys())
        self._i = iter(columns)
        return self

    def __next__(self):
        columns = six.advance_iterator(self._i)
        return columns, getattr(self, columns)

    def _as_dict(self):
        return {k: v for k, v in self}

    def iteritems(self):
        return six.iteritems(self._as_dict())

    def items(self):
        return self._as_dict().items()

    def keys(self):
        return self._as_dict().keys()


class TimestampMixin(object):
    created_at = Column(DateTime, default=lambda: datetime.utcnow())
    updated_at = Column(DateTime, onupdate=lambda: datetime.utcnow())


class SoftDeleteMixin(object):
    deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)

    def soft_delete(self, session):
        self.deleted = True
        self.deleted_at = datetime.utcnow()
        self.save(session)
