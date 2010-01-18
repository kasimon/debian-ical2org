#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2009 Doug Hellmann.  All rights reserved.
#
"""
"""
import ConfigParser

from ical2org import format, tz

class OrgTreeFormatter(format.CalendarFormatter):
    """Formats output as an org outline.
    """

    def __init__(self, output, config, options):
        format.CalendarFormatter.__init__(self, output, config, options)
        self.output.write('# -*- coding: utf-8 -*-\n')
        return
    
    def start_calendar(self, calendar):
        """Begin a calendar node.
        
        Arguments:
        - `self`:
        - `calendar`:
        """
        self.active_calendar = calendar
        self.output.write('* %s' % calendar.title)
        try:
            tags = self.config.get(calendar.title, 'tags')
            tags = tags.strip(':')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            pass
        else:
            self.output.write('\t:%s:' % tags)
        self.output.write('\n')
        try:
            category = self.config.get(calendar.title, 'category')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            category = calendar.title
        self.output.write('  :CATEGORY: %s\n' % category)
        return

    def format_event(self, event):
        event_start = event.dtstart.value.astimezone(tz.local)
        event_end = event.dtend.value.astimezone(tz.local)
        if event_start.date() == event_end.date():
            time_range = '<%s-%s>' % (event_start.strftime('%Y-%m-%d %a %H:%M'),
                                      event_end.strftime('%H:%M'))
        else:
            time_range = '<%s>--<%s>' % (event_start.strftime('%Y-%m-%d %a %H:%M'),
                                              event_end.strftime('%Y-%m-%d %a %H:%M'))

        lines = ['** %s\n   %s' % (event.summary.value, time_range) ]

        if getattr(event, 'location', None):
            lines.append('   - Location: %s' % event.location.value)

# Unicode error for PyATL calendar events.
        if getattr(event, 'description', None):
            desc_lines = event.description.value.splitlines()
            lines.append('   - %s' % desc_lines[0])
            lines.extend([ '     %s' % l for l in desc_lines[1:]])

        lines.append('')
        return '\n'.join(lines)
    



        

