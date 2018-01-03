from sqlalchemy import Column, ForeignKey, MetaData, String, Table


meta = MetaData()

person = Table(
    'person', meta,
    Column('id', String(36), primary_key=True, nullable=False),
    Column('name', String(250), nullable=False)
)

address = Table(
    'address', meta,
    Column('id', String(36), primary_key=True, nullable=False),
    Column('address_line', String(250)),
    Column('postal_code', String(10), nullable=False),
    Column('person_id', String(36), ForeignKey('person.id'), nullable=False)
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta.bind = migrate_engine
    person.create()
    address.create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    person.drop()
    address.drop()
