import functools
import datetime
import inspect
import json
import six
import uuid

PERFECT_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

_nasty_type_tests = [inspect.ismodule, inspect.isclass, inspect.ismethod,
                     inspect.isfunction, inspect.isgeneratorfunction,
                     inspect.isgenerator, inspect.istraceback, inspect.isframe,
                     inspect.iscode, inspect.isbuiltin, inspect.isroutine,
                     inspect.isabstract]

_simple_types = (six.text_type, six.integer_types, type(None), bool, float)


def to_primitive(value, convert_instances=False,
                 level=0, max_depth=3, encoding='utf-8'):
    if isinstance(value, _simple_types):
        return value

    if isinstance(value, six.binary_type):
        if six.PY3:
            value = value.decode(encoding=encoding)
        return value

    if isinstance(value, datetime.datetime):
        return value.strftime(PERFECT_TIME_FORMAT)

    if isinstance(value, uuid.UUID):
        return six.text_type(value)

    if any(test(value) for test in _nasty_type_tests):
        return six.text_type(value)

    if level > max_depth:
        return None

    try:
        recursive = functools.partial(to_primitive,
                                      convert_instances=convert_instances,
                                      level=level,
                                      max_depth=max_depth,
                                      encoding=encoding)
        if isinstance(value, dict):
            return {recursive(k): recursive(v)
                    for k, v in value.items()}
        elif hasattr(value, 'iteritems'):
            return recursive(dict(value.iteritems()), level=level + 1)
        # Python 3 does not have iteritems
        elif hasattr(value, 'items'):
            return recursive(dict(value.items()), level=level + 1)
        elif hasattr(value, '__iter__'):
            return list(map(recursive, value))
        elif convert_instances and hasattr(value, '__dict__'):
            return recursive(value.__dict__, level=level + 1)
    except TypeError:
        return six.text_type(value)
    return value


def dumps(obj, default=to_primitive, encoding='utf-8'):
    serialized = json.dumps(obj, default=default)
    if isinstance(serialized, six.text_type):
        serialized = serialized.encode(encoding)
    return serialized


def loads(text, encoding='utf-8'):
    if not isinstance(text, (six.string_types, six.binary_type)):
        raise TypeError("%s can't be decoded" % type(text))
    if not isinstance(text, six.text_type):
        text = text.decode(encoding)
    return json.loads(text, encoding)
