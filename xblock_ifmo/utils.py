# -*- coding=utf-8 -*-

import collections
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


def datetime_mapper(x, date_format):
    """

    :param x:
    :return:
    """

    def transform_value(value):
        if isinstance(value, dict):
            return datetime_mapper(value, date_format)
        elif isinstance(value, datetime.datetime):
            return value.strftime(date_format)
        else:
            return value

    return dict(map(lambda (key, val): (key, transform_value(val)), x.items()))


def deep_update(d, u):
    for k, v in u.iteritems():
        if isinstance(d, collections.MutableMapping):
            if isinstance(v, collections.Mapping):
                r = deep_update(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        else:
            d = {k: u[k]}
    return d
