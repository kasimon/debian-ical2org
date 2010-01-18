# encoding: utf-8
#
# Copyright (c) 2009 Doug Hellmann.  All rights reserved.
#
"""Diary file formatter
"""

import datetime
import logging

import vobject

from ical2org import tz, format

log = logging.getLogger(__name__)

class DiaryFormatter(format.CalendarFormatter):
    """Produces output in emacs diary format.
    """

    calendar_title = None
    def start_calendar(self, calendar):
        """Saves the calendar title.
        """
        self.calendar_title = calendar.title
        return

    def format_event(self, event):
        event_start = event.dtstart.value
        event_end = event.dtend.value
        if not isinstance(event_start, datetime.datetime):
            log.debug('rebuilding dates')
            event_start = datetime.datetime.combine(event_start, datetime.time.min).replace(tzinfo=tz.local)
            event_end = datetime.datetime.combine(event_end, datetime.time.max).replace(tzinfo=tz.local)

        event_start = event_start.astimezone(tz.local)
        event_end = event_end.astimezone(tz.local)

        if event_start.date() == event_end.date():
            # MM/DD/YY HH:MM-HH:MM summary (calendar title)
            start = event_start.strftime('%m/%d/%y %H:%M')
            end = event_end.strftime('%H:%M')
            response = '%s-%s %s' % (start, end, event.summary.value)
        else:
            # %%(diary-block MM DD YYYY MM DD YYYY) summary (calendar title)
            start = event_start.strftime('%m %d %Y')
            end = event_end.strftime('%m %d %Y')
            response = '%%%%(diary-block %s %s) %s' % (start, end, event.summary.value)
        if self.calendar_title:
            response = '%s (%s)' % (response, self.calendar_title)
        return response + '\n'

