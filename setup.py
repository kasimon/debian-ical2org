#!/usr/bin/env python

from setuptools import setup, find_packages

PROJECT = 'ical2org'
VERSION = '1.0'

try:
    long_description = open('README', 'rt').read()
except IOError:
    long_description = ''

setup(
    name = PROJECT,
    description = 'Convert iCal files to emacs org-mode data',
    long_description = long_description,
    version = VERSION,

    # Meta-data
    author = 'Doug Hellmann',
    author_email = 'doug.hellmann@gmail.com',
    url = 'http://www.doughellmann.com/projects/ical2org/',
    download_url = 'http://www.doughellmann.com/downloads/%s-%s.tar.gz' % \
        (PROJECT, VERSION),
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Communications',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: Scheduling',
        ],

    # What goes into the distribution?
    packages = find_packages(),
    include_package_data = True,
    entry_points = {
        'console_scripts': [ 'ical2org = ical2org.app:main' ],
        },

    # What do we need to work?
    install_requires=[
        'distribute',
        'pytz>=2009r',
        'vobject>=0.8.1c',
        ],
    )
