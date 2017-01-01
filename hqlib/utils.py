"""
Copyright 2012-2017 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from __future__ import division


import datetime
import json
import re


MONTHS = {
    1: 'januari',
    2: 'februari',
    3: 'maart',
    4: 'april',
    5: 'mei',
    6: 'juni',
    7: 'juli',
    8: 'augustus',
    9: 'september',
    10: 'oktober',
    11: 'november',
    12: 'december',
}

ABBREVIATED_MONTHS = {
    'jan':  1,
    'feb':  2,
    'mar':  3, 'mrt': 3,
    'apr':  4,
    'may':  5, 'mei':  5,
    'jun':  6,
    'jul':  7,
    'aug':  8,
    'sep':  9,
    'oct': 10, 'okt': 10,
    'nov': 11,
    'dec': 12
}


_YEAR_RE = "(?P<year>[0-9]{4})"
_MONTHNAME_RE = "(?P<monthname>[A-Z][a-z][a-z])"
_MONTH_RE = "(?P<month>[0-9]{1,2})"
_DAY_RE = "(?P<day>[0-9]{1,2})"
_DAYNAME_RE = "(?P<dayname>[A-Z][a-z]*)"
_TIME_RE = "(?P<hour>[0-9]{1,2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2})"
_AM_PM_RE = "(?P<am_pm>[AP]M)"
_TIMEZONE_RE = "(?P<tzname>[A-Z]{3,4})"

# US format: 'Apr 5, 2013 10:04:10 AM'
_US_DATE_TIME_RE = _MONTHNAME_RE + r"\s+" + _DAY_RE + r",\s+" + _YEAR_RE + r"\s+" + _TIME_RE + r"\s+" + _AM_PM_RE
# UK format: 'Tue Apr 5 2013 22:10:10 CEST'
_UK_DATE_TIME_RE = r"\s+".join([_DAYNAME_RE, _MONTHNAME_RE, _DAY_RE, _YEAR_RE, _TIME_RE, _TIMEZONE_RE])
# UK format, year last: 'Tue Apr 5 22:10:10 CEST 2013'
_UK_DATE_TIME_YEAR_LAST_RE = r"\s+".join([_DAYNAME_RE, _MONTHNAME_RE, _DAY_RE, _TIME_RE, _TIMEZONE_RE, _YEAR_RE])
# ISO date: '2013-11-05'
_ISO_DATE_RE = "-".join([_YEAR_RE, _MONTH_RE, _DAY_RE])


def _parse_date_time(date_time_re, date_time_string):
    """ Parse a date/time string using a regular expression. The regular expression must contain named match groups:
        year - the year in four digits
        monthname - the abbreviate name of the month
        day - the number of the day in the month
        hour, minute, second - the time
        and optional:
        am_pm - used insensitive to case
        """
    match = re.search(date_time_re, date_time_string)
    if match is None:
        raise ValueError("date_time_string {s!r} not matched".format(s=date_time_string))

    year = int(match.group('year'))
    month = ABBREVIATED_MONTHS[match.group('monthname').lower()]
    day = int(match.group('day'))
    hour = int(match.group('hour'))
    minute = int(match.group('minute'))
    second = int(match.group('second'))
    if match.groupdict().get('am_pm', '').lower() == 'pm' and hour < 12:
        hour += 12

    return datetime.datetime(year, month, day, hour, minute, second)


def parse_us_date_time(date_time_string):
    """ Parse a US format date/time string of the form 'Apr 5, 2013 10:04:10 AM'. """
    return _parse_date_time(_US_DATE_TIME_RE, date_time_string)


def parse_uk_date_time_year_last(date_time_string):
    """ Parse a UK format date/time string of the form 'Mon Aug 24 2015 16:05:55 CEST'. """
    return _parse_date_time(_UK_DATE_TIME_YEAR_LAST_RE, date_time_string)


def parse_iso_date(date_string):
    """ Parse an ISO format date string of the form '2013-11-05'. """
    match = re.search(_ISO_DATE_RE, date_string)
    if match is None:
        raise ValueError("date_string {s!r} not matched".format(s=date_string))

    year = int(match.group('year'))
    month = int(match.group('month'))
    day = int(match.group('day'))

    return datetime.datetime(year, month, day)


def parse_iso_datetime(datetime_string):
    """ Parse an ISO format date time string of the form '2015-10-06T15:00:01Z'. """
    return datetime.datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%SZ')


def percentage(numerator, denominator, zero_divided_by_zero_is_zero=False):
    """ Return numerator / denominator * 100. """
    if float(denominator) == 0.0:
        return 0 if float(numerator) == 0.0 and zero_divided_by_zero_is_zero else 100
    else:
        return int(round((numerator / denominator) * 100))


def format_date(date_time, year=None):
    """ Return a (Dutch) formatted version of the datetime. """
    if date_time:
        formatted_date = '{day} {month}'.format(day=date_time.day, month=MONTHS[date_time.month])
        if year:
            formatted_date += ' {year}'.format(year=date_time.year)
    else:
        formatted_date = 'onbekende datum'
    return formatted_date


def format_timedelta(timedelta):
    """ Return a (Dutch) formatted version of the timedelta. """

    days = timedelta.days
    hours = timedelta.seconds // 3600
    minutes = (timedelta.seconds % 3600) // 60

    for unit, unit_singular, unit_plural in (days, 'dag', 'dagen'), (hours, 'uur', 'uur'), \
                                            (minutes, 'minuut', 'minuten'):
        if unit:
            return '{0} {1}'.format(unit, unit_plural) if unit > 1 else 'een {0}'.format(unit_singular)
    return 'minder dan een minuut'


def workdays_in_period(start_date, end_date):
    """ Return the number of work days in the period. All days between start date and end date are considered,
        including the start date and end date themselves. """
    return sum(1 for ordinal in range(start_date.toordinal(), end_date.toordinal() + 1)
               if datetime.date.fromordinal(ordinal).isoweekday() <= 5)


class memoized(object):  # pylint: disable=invalid-name,too-few-public-methods
    """ Decorator. Caches a function's return value each time it is called. If called later with the same arguments,
        the cached value is returned (not reevaluated). """

    def __init__(self, func):
        self.__func = func
        self.__instance = None
        self.__cache = {}

    def __get__(self, instance, cls=None):
        self.__instance = instance
        return self

    def __call__(self, *args, **kwargs):
        key = (id(self.__instance),) + args + tuple([kwargs[key] for key in sorted(kwargs)])
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
        """ Return the function's docstring. """
        return self.__func.__doc__


def html_escape(text):
    """ Return the text with all HTML characters escaped. """
    for character, html_code in [('&', '&amp;'), ('"', '&quot;'), ("'", '&#39;'), (">", '&gt;'), ("<", '&lt;')]:
        text = text.replace(character, html_code)
    return text


def eval_json(json_string):
    """ Return an evaluated version of the json string. """
    return json.loads(json_string)


def version_number_to_numerical(version_number_tuple):
    """ Transform the first three parts (major, minor, patch) of the version number into a numerical value.
        We assume each part is not larger than 100, so that 10000 * major + 100 * minor + patch results in a number
        for which holds that numerical_value(a.b.c.) > numerical_value(d.e.f) iff a.b.c > d.e.f. """
    result = 0
    for part, factor in zip(version_number_tuple[:3], (10000, 100, 1)):
        result += part * factor
    return result
