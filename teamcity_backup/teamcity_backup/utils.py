# -*- coding: utf-8 -*-

""""""

import logging

from functools import wraps

__all__ = [
    'log_step',
]


def log_step(_func=None, name=None, logger=None):
    def decorator_log_step(f):
        log = logger or logging.getLogger(__package__)
        nm = name or f.__name__

        @wraps(f)
        def wrapper(*args, **kwargs):
            log.info(f'Start "{nm}"...')
            res = f(*args, **kwargs)
            log.info(f'Finish "{nm}"')
            return res
        return wrapper

    if _func is None:
        return decorator_log_step
    else:
        return decorator_log_step(_func)
