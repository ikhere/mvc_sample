import uuid

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from mvc import exceptions
from mvc import settings
from mvc.db import models

session_maker = None


def get_engine(url=settings.DATABASE_URL):
    return create_engine(url)


def get_session(engine=None):
    global session_maker
    if not session_maker:
        engine = engine or get_engine()
        session_maker = sessionmaker(bind=engine, autocommit=True)
    return session_maker()


def dispose_engine():
    get_engine().dispose()


def model_query(model):
    session = get_session()
    query = session.query(model)
    return query


def person_get_all():
    return model_query(models.Person).all()


def person_get(person_id):
    result = model_query(models.Person).filter_by(id=person_id).first()

    if not result:
        raise exceptions.PersonNotFound(reference=person_id)

    return result


def person_create(values):
    person_ref = models.Person()
    if 'id' not in values:
        values['id'] = str(uuid.uuid4())
    session = get_session()
    person_ref.update(values)
    person_ref.save(session)
    return person_get(person_ref.id)


def person_update(person_id, values):
    person_ref = person_get(person_id)
    session = get_session()
    person_ref.update(values)
    person_ref.save(session)
    return person_get(person_id)


def person_delete(person_id):
    session = get_session()
    person_ref = person_get(person_id)
    person_ref.delete(session)
