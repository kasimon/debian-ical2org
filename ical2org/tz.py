#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2009 Doug Hellmann.  All rights reserved.
#
"""
"""

from datetime import datetime, date

import dateutil

utc = dateutil.tz.tzutc()

local = dateutil.tz.tzlocal()

def normalize_to_utc(dt):
    """
    """
    if not isinstance(dt, date):
        raise TypeError("%r is not a datetime.date instance" % (dt,))

    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            # Assume local time zone
            dt = dt.replace(tzinfo=local)
        return dt.astimezone(utc)
    return dt

