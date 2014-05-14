'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import calendar
import datetime
import logging
import os
import shutil
import json


MONTHS = {1: 'januari', 2: 'februari', 3: 'maart', 4: 'april', 5: 'mei', 
          6: 'juni', 7: 'juli', 8: 'augustus', 9: 'september', 10: 'oktober', 
          11: 'november', 12: 'december'}

ABBREVIATED_MONTHS = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5,
                      'mei': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 
                      'oct': 10, 'okt': 10, 'nov': 11, 'dec': 12}


def parse_us_date_time(date_time_string):
    ''' Parse a US format date/time string of the form 
        'Apr 5, 2013 10:04:10 AM'. '''
    date_time_components = date_time_string.strip().split(' ')
    month = ABBREVIATED_MONTHS[date_time_components[0].lower()]
    day = int(date_time_components[1].strip(','))
    year = int(date_time_components[2])
    hour, minute, second = parse_time_string(date_time_components[3])
    am_pm = date_time_components[4]
    if am_pm.lower() == 'pm' and hour < 12:
        hour += 12
    return datetime.datetime(year, month, day, hour, minute, second)


def parse_uk_date_time(date_time_string):
    ''' Parse a UK format date/time string of the form 
        'Tue Apr 5 22:10:10 CEST 2013'. '''
    date_time_components = date_time_string.strip().split(' ')
    month = ABBREVIATED_MONTHS[date_time_components[1].lower()]
    day = int(date_time_components[2])
    hour, minute, second = parse_time_string(date_time_components[3])
    year = int(date_time_components[5])
    return datetime.datetime(year, month, day, hour, minute, second)


def parse_iso_date_time(date_time_string):
    ''' Parse an ISO format date/time string of the form
        '2012-10-24T16:20:16.000+0200'. '''
    return datetime.datetime.strptime(date_time_string, '%Y-%m-%dT%H:%M:%S.%f')


def parse_iso_date(date_string):
    ''' Parse an ISO format date string of the form '2013-11-05'. '''
    year, month, day = date_string.split('-')
    return datetime.datetime(int(year), int(month), int(day))


def parse_time_string(time_string):
    ''' Parse a time string of the form '22:10:34'. '''
    time_components = time_string.split(':')
    hour, minute, second = (int(component) for component in time_components)
    return hour, minute, second


def parse_us_int(string):
    ''' Remove , from US format integers. '''
    return int(string.replace(',', ''))


def percentage(numerator, denominator, zero_divided_by_zero_is_zero=False):
    ''' Return numerator / denominator * 100. '''
    if float(denominator) == 0.0:
        if float(numerator) == 0.0 and zero_divided_by_zero_is_zero:
            return 0
        else: 
            return 100
    else:
        return round((float(numerator) / float(denominator)) * 100)


def format_date(date_time, year=False):
    ''' Return a (Dutch) formatted version of the datetime. '''
    if date_time:
        formatted_date = '%d %s' % (date_time.day, MONTHS[date_time.month])
        if year:
            formatted_date += ' %s' % date_time.year
    else:
        formatted_date = 'onbekende datum'
    return formatted_date


def format_month(date):
    ''' Return a (Dutch) formatted version of the month and year. '''
    return '%s %d' % (MONTHS[date.month], date.year)


def format_timedelta(timedelta):
    ''' Return a (Dutch) formatted version of the timedelta. '''

    def format_days_and_hours(timedelta):
        ''' Return a (Dutch) formatted version of a timedelta in days and
            hours. '''
        days = timedelta.days
        hours = timedelta.seconds / 3600
        if days > 1:
            return '%d dagen' % days
        if hours > 0:
            return 'een dag en %d uur' % hours
        else:
            return '24 uur'

    def format_hours_and_minutes(timedelta):
        ''' Return a (Dutch) formatted version of a timedelta in hours and
            minutes. '''
        hours = timedelta.seconds / 3600
        minutes = (timedelta.seconds % 3600) / 60
        if hours > 0:
            result = '%d uur' % hours
            if hours < 3 and minutes > 1:
                result += ' en %d minuten' % minutes
            return result
        else:
            if minutes > 1:
                return '%d minuten' % minutes
            else:
                return 'een minuut'

    if timedelta.days > 0:
        return format_days_and_hours(timedelta)
    else:
        return format_hours_and_minutes(timedelta)


def month_ago(date=None, day_correction=0):
    ''' Return the date that is one month earlier on the same day of the 
        month (or earlier if needed to prevent invalid days). '''
    date = date or datetime.date.today()
    month = date.month - 1
    year = date.year
    day = date.day - day_correction
    if month == 0:
        month = 12
        year -= 1
    try:
        return date.replace(year=year, month=month, day=day)
    except ValueError:
        return month_ago(date, day_correction + 1)


def last_day_of_month(date):
    ''' Return the day number of the last of the month. '''
    if date.month == 2:
        return 29 if calendar.isleap(date.year) else 28
    else:
        return 31 if date.month in (1, 3, 5, 7, 8, 10, 12) else 30


def workdays_in_period(start_date, end_date):
    ''' Return the number of work days in the period. All days between
        start date and end date are considered, including the start date and
        end date themselves. '''
    workday_count = 0
    for ordinal in range(start_date.toordinal(), end_date.toordinal() + 1):
        day = datetime.date.fromordinal(ordinal)
        if day.isoweekday() <= 5:
            workday_count += 1
    return workday_count


class memoized(object):  # pylint: disable=C0103,R0903
    ''' Decorator. Caches a function's return value each time it is called.
        If called later with the same arguments, the cached value is returned
        (not reevaluated). '''

    def __init__(self, func):
        self.__func = func
        self.__instance = None
        self.__cache = {}

    def __get__(self, instance, cls=None):
        self.__instance = instance
        return self

    def __call__(self, *args, **kwargs):
        key = (id(self.__instance),) + args + \
              tuple([kwargs[key] for key in sorted(kwargs)])
        try:
            return self.__cache[key]
        except KeyError:
            value = self.__func(self.__instance, *args, **kwargs)
            self.__cache[key] = value
            return value
        except TypeError:
            # Not cacheable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.__func(self.__instance, *args, **kwargs)

    def __repr__(self):
        ''' Return the function's docstring. '''
        return self.__func.__doc__


def rmtree(folder, remove_tree=shutil.rmtree, exists=os.path.exists):
    ''' Remove folder recursively. '''
    if exists(folder):
        try:
            remove_tree(folder)
        except OSError, reason:
            logging.warning("Couldn't remove %s: %s", folder, reason)


def html_escape(text):
    '''Return the text with all HTML characters escaped. '''
    text = text.replace('&', '&amp;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#39;')
    text = text.replace(">", '&gt;')
    text = text.replace("<", '&lt;')
    return text


def eval_json(json_string):
    ''' Return an evaluated version of the json string. '''
    return json.loads(json_string)
