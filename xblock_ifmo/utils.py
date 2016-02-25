# -*- coding=utf-8 -*-

from django.core.exceptions import PermissionDenied

import datetime
import pytz


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
