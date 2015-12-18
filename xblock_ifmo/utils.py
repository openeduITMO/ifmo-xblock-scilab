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
