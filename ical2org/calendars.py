#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2009 Doug Hellmann.  All rights reserved.
#
"""Utilities for working with calendar files
"""

import datetime
from glob import glob
import logging
import os
import plistlib

import vobject

from ical2org import tz

log = logging.getLogger(__name__)

def _get_candidate_directories(path):
    """Return a list of directory names under path
    that look like they might be calendars.
    """
    calendar_directories = (
        glob(os.path.join(path, '*.caldav', '*.calendar')) +
        glob(os.path.join(path, '*.calendar'))
        )
    return calendar_directories


def discover(path, active_only):
    """Generator that yields Calendar instances.

    path is a string refering to the directory to search for
    calendars.
    
    active_only is a boolean controlling whether only calendars
    checked in iCal are included in the output.
    """
    for dirname in _get_candidate_directories(path):
        try:
            c = Calendar(dirname)
        except ValueError:
            continue
        if active_only and not c.active:
            continue
        yield c
    

def get_by_titles(path, titles):
    """Generator that yields the named Calendar instances.

    path is a string refering to the directory to search for
    calendars.
    
    titles is a list of strings of the titles of the calendars.
    """
    for dirname in _get_candidate_directories(path):
        try:
            c = Calendar(dirname)
        except ValueError:
            continue
        if c.title in titles:
            yield c


class Calendar(object):
    """Simple calendar wrapper."""
    def __init__(self, path):
        self.path = path
        log.debug('Trying to load calendar in %s', path)
        info_file = os.path.join(path, 'Info.plist')
        if not os.path.isfile(info_file):
            raise ValueError('%s does not look like a calendar' % path)
        self.info = plistlib.readPlist(info_file)
        self.title = self.info.get('Title')
        self.active = self.info.get('Checked')
        log.debug('Calendar "%s" (active=%s)', self.title, self.active)
        return

    def get_events(self):
        """Generator that yields all events in the calendar.
        """
        ics_filenames = glob(os.path.join(self.path, 'Events', '*.ics'))
        for ics_filename in ics_filenames:
            with open(ics_filename, 'rt') as ics_file:
                for component in vobject.readComponents(ics_file):
                    for event in component.vevent_list:
                        #event.prettyPrint()
                        event.dtstart.value = tz.normalize_to_utc(event.dtstart.value)
                        event.dtend.value = tz.normalize_to_utc(event.dtend.value)
                        #event.prettyPrint()
                        yield event
        return
