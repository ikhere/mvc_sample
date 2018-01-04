from sqlalchemy import Boolean, DateTime, Column, ForeignKey, MetaData, String
from sqlalchemy import Table


def define_tables(meta):
    person = Table(
        'person', meta,
        Column('id', String(36), primary_key=True, nullable=False),
        Column('name', String(250), nullable=False),
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        Column('deleted_at', DateTime),
        Column('deleted', Boolean)
    )

    address = Table(
        'address', meta,
        Column('id', String(36), primary_key=True, nullable=False),
        Column('address_line', String(250)),
        Column('postal_code', String(10), nullable=False),
        Column('person_id', String(36), ForeignKey('person.id'),
               nullable=False),
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        Column('deleted_at', DateTime),
        Column('deleted', Boolean)
    )
    return person, address


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    tables = define_tables(meta)
    for table in tables:
        table.create()


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    tables = define_tables(meta)
    for table in tables:
        table.drop()
