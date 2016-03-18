# -*- coding=utf-8 -*-

import datetime
import pytz

from django.core.exceptions import PermissionDenied


def require(condition):
    if not condition:
        raise PermissionDenied


def now():
    """
    Текущее время в UTC, tz-aware.

    :return: Время в UTC
    """
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


def default_time(fn):
    # TODO: This decorator cannot be loaded form ifmo_xblock.utils. WHY?!
    def default_timed(**kwargs):
        qtime = kwargs.get('qtime')
        if qtime is None:
            qtime = now()
        kwargs['qtime'] = qtime
        return fn(**kwargs)
    return default_timed


def reify(meth):
    """
    Decorator which caches value so it is only computed once.
    Keyword arguments:
    inst
    """
    def getter(inst):
        """
        Set value to meth name in dict and returns value.
        """
        value = meth(inst)
        inst.__dict__[meth.__name__] = value
        return value
    return property(getter)
