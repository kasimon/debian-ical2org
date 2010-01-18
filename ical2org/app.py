# encoding: utf-8
#
# Copyright (c) 2009 Doug Hellmann.  All rights reserved.
#
"""Command line interface for ical2org.
"""

import codecs
from ConfigParser import SafeConfigParser as ConfigParser
import datetime
import inspect
import logging
import optparse
import os
import sys

from ical2org import calendars, filter, diary, tz, org

import vobject

VERBOSE_LEVELS = {
    0:logging.WARNING,
    1:logging.INFO,
    2:logging.DEBUG,
    }

FORMATTER_FACTORIES = {
    'diary':diary.DiaryFormatter,
    'org':org.OrgTreeFormatter,
    }

def remember_formatter_option(option, opt_str, value, parser):
    """Receive and handle a formatter-specific option.
    
    :param option: The parsed option results.
    :param opt_str: The option string from the command line.
    :param value: The option value.  Should be ``name=value``.
    :param parser: The option parser.
    """
    if not hasattr(option, 'formatter_options'):
        option.formatter_options = {}
    parsed = value.split('=', 1)
    if len(parsed) == 1:
        # flag
        option.formatter_options[value] = True
    else:
        # name=value
        opt_name, opt_val = parsed
        option.formatter_options[opt_name] = opt_val
    return

def show_verbose_help(option, opt_str, value, parser):
    parser.print_help()
    print '\nFormatters:\n'
    for name, formatter in sorted(FORMATTER_FACTORIES.items()):
        print name
        print '-' * len(name)
        print inspect.getdoc(formatter)
    parser.exit()
    return

def main(args=sys.argv[1:]):
    option_parser = optparse.OptionParser(
        usage='usage: ical2org [options] [calendar titles]',
        conflict_handler='resolve',
        description='Convert iCal calendar entries to org-mode data for use with emacs',
        )
    option_parser.add_option('-c', '--config',
                             action='store',
                             dest='config_filename',
                             help='Configuration file name. Defaults to ~/.ical2org',
                             default=os.path.expanduser('~/.ical2org'),
                             )
    option_parser.add_option('--begin', '-b', '--days-ago',
                             action='store',
                             dest='days_ago',
                             help='Number of days back in time to search. Defaults to 14.',
                             default=14,
                             type=int,
                             )
    option_parser.add_option('--end', '-e', '--days-ahead',
                             action='store',
                             dest='days_ahead',
                             help='Number of days forward in time to search. Defaults to 30.',
                             default=30,
                             type=int,
                             )
    option_parser.add_option('-v', '--verbose',
                             action='count',
                             dest='verbose_level',
                             default=1,
                             help='Increase verbose level',
                             )
    option_parser.add_option('-q', '--quiet',
                             action='store_const',
                             const=0,
                             dest='verbose_level',
                             help='Turn off verbose output',
                             )
    option_parser.add_option('--output-file', '-o',
                             action='store',
                             dest='output_file_name',
                             help='Write the output to the named file instead of stdout',
                             default=None,
                             )
    option_parser.add_option('--all',
                             action='store_false',
                             dest='active_only',
                             default=True,
                             help='Include all calendars, not just active.',
                             )
    option_parser.add_option('--input-directory',
                             action='store',
                             dest='input_directory',
                             default=os.path.expanduser('~/Library/Calendars'),
                             help='Directory containing calendars. Defaults to ~/Library/Calendars.',
                             )
    option_parser.add_option('--format', '-f',
                             action='store',
                             dest='format',
                             type='choice',
                             choices=FORMATTER_FACTORIES.keys(),
                             default='org',
                             help='Output format. One of %s. Defaults to "diary".' % FORMATTER_FACTORIES.keys(),
                             )
    option_parser.add_option('--opt', '--formatter-option',
                             action='callback',
                             type='string',
                             callback=remember_formatter_option,
                             help='Formatter-specific option name=value',
                             )
    option_parser.add_option('--help',
                             action='callback',
                             callback=show_verbose_help,
                             help='Verbose help',
                             )
                             
    options, calendar_titles = option_parser.parse_args(args)

    log_level = VERBOSE_LEVELS.get(options.verbose_level, logging.DEBUG)
    logging.basicConfig(level=log_level, format='%(message)s')

    config = ConfigParser()
    config.read([options.config_filename])

    # Compute the date range for items to be included in our output.
    start_date = tz.normalize_to_utc(datetime.datetime.combine(
        datetime.date.today() - datetime.timedelta(options.days_ago),
        datetime.time.min,
        ))
    end_date = tz.normalize_to_utc(datetime.datetime.combine(
        datetime.date.today() + datetime.timedelta(options.days_ahead + 1),
        datetime.time.min,
        ))
    logging.info('Starting %d days ago at %s', options.days_ago, start_date.astimezone(tz.local))
    logging.info('Ending %d days from now at %s', options.days_ahead, end_date.astimezone(tz.local))

    if options.output_file_name:
        logging.info('Writing to %s', options.output_file_name)

    # Load the calendars
    if calendar_titles:
        calendar_generator = calendars.get_by_titles(path=options.input_directory,
                                                     titles=calendar_titles)
    else:
        calendar_generator = calendars.discover(path=options.input_directory,
                                                active_only=options.active_only)

    # Process the calendar data
    output = sys.stdout
    if options.output_file_name:
        output = codecs.open(options.output_file_name, 'wt', 'UTF-8')
    try:
        formatter = FORMATTER_FACTORIES[options.format](output, config, options)
        for calendar in calendar_generator:
            logging.info('Processing: %s', calendar.title)
            formatter.start_calendar(calendar)
            for event in filter.unique(filter.by_date_range(calendar.get_events(),
                                                            start_date,
                                                            end_date,
                                                            )):
                logging.info('  %s', event.summary.value)
                formatter.add_event(event)
            formatter.end_calendar(calendar)
    finally:
        formatter.close()
        if output != sys.stdout:
            output.close()
    return
    
    
if __name__ == '__main__':
    main()
