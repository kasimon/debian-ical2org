#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2009 Doug Hellmann.  All rights reserved.
#
"""Filter events by a date range.
"""

import datetime
import logging
import sys

import vobject

from ical2org import tz

log = logging.getLogger(__name__)

def by_date_range(events, start, end):
    """Iterate over the incoming events and yield those that fall within the date range.
    """
    log.debug('filtering between %s and %s', start, end)
    for event in events:

        # Fix time zones in date objects
        event_start = event.dtstart.value
        event_end = event.dtend.value
        if not isinstance(event_start, datetime.datetime):
            event_start = datetime.datetime.combine(event.dtstart.value,
                                                    datetime.time.min,
                                                    )
            if event_start == event_end:
                event_end = datetime.datetime.combine(event.dtend.value,
                                                      datetime.time.max,
                                                      )
            else:
                event_end = datetime.datetime.combine(event.dtend.value,
                                                      datetime.time.min,
                                                      )
                

        event_start = tz.normalize_to_utc(event_start)
        event_end = tz.normalize_to_utc(event_end)

        # Replace the dates in case we updated the timezone
        event.dtstart.value = event_start
        event.dtend.value = event_end
        
#         event.prettyPrint()
#         sys.stdout.flush()
        
        event_rrule = getattr(event, 'rrule', None)
        log.debug('checking %s - %s == %s',
                  event.dtstart.value,
                  event.dtend.value,
                  event.summary.value,
                  )
        if event_rrule is not None:
            duration = event.dtend.value - event.dtstart.value
            rruleset = event.getrruleset(False)

            # Clean up timezone values in rrules.
            # Based on ShootQ calendarparser module.
            for rrule in rruleset._rrule:
                # normalize start and stop dates for each recurrance
                if rrule._dtstart:
                    rrule._dtstart = tz.normalize_to_utc(rrule._dtstart)
                if hasattr(rrule, '_dtend') and rrule._dtend:
                    rrule._dtend = tz.normalize_to_utc(rrule._dtend)
                if rrule._until:
                    rrule._until = tz.normalize_to_utc(rrule._until)
            if rruleset._exdate:
                # normalize any exclusion dates
                exdates = []
                for exdate in rruleset._exdate:
                    exdate = tz.normalize_to_utc(exdate)
                rruleset._exdate = exdates
            if hasattr(rruleset, '_tzinfo') and rruleset._tzinfo is None:
                # if the ruleset doesn't have a time zone, give it
                # the local zone
                rruleset._tzinfo = tz.local

            # Explode the event into repeats
            for recurrance in rruleset.between(start, end, inc=True):
                log.debug('  recurrance %s', recurrance)
                dupe = event.__class__.duplicate(event)
                dupe.dtstart.value = tz.normalize_to_utc(recurrance)
                dupe.dtend.value = tz.normalize_to_utc(recurrance + duration)
                yield dupe
                
        elif event_start >= start and event_end <= end:
            yield event
        
    
def unique(events):
    """Filter out duplicate events based on uid and start time.
    """
    keys = set()
    for event in events:
        key = (event.uid.value, event.dtstart.value)
        if key not in keys:
            keys.add(key)
            yield event
        else:
            log.debug('found duplicate event %s', key)
