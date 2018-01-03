import logging

_loggers = {}


def get_logger(name=None):
    name = name or 'mvc'
    if name not in _loggers:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        _loggers[name] = logging.LoggerAdapter(logger, None)
    return _loggers[name]
