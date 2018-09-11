"""
Copyright 2012-2018 Ministerie van Sociale Zaken en Werkgelegenheid

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


from typing import Any, Tuple, Union
import datetime
import json
import logging
import re

from hqlib.typing import DateTime, TimeDelta, Number


# Constants

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
    'jan': 1,
    'feb': 2,
    'mar': 3, 'mrt': 3,
    'apr': 4,
    'may': 5, 'mei': 5,
    'jun': 6,
    'jul': 7,
    'aug': 8,
    'sep': 9,
    'oct': 10, 'okt': 10,
    'nov': 11,
    'dec': 12
}


_YEAR_RE = "(?P<year>[0-9]{4})"
_MONTHNAME_RE = "(?P<monthname>[A-Z][a-z][a-z])"
_MONTH_RE = "(?P<month>[0-9]{1,2})"
_DAY_RE = "(?P<day>[0-9]{1,2})"
_TIME_RE = "(?P<hour>[0-9]{1,2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2})"
_AM_PM_RE = "(?P<am_pm>[AP]M)"

# US format: 'Apr 5, 2013 10:04:10 AM'
_US_DATE_TIME_RE = _MONTHNAME_RE + r"\s+" + _DAY_RE + r",\s+" + _YEAR_RE + r"\s+" + _TIME_RE + r"\s+" + _AM_PM_RE
# ISO date: '2013-11-05'
_ISO_DATE_RE = "-".join([_YEAR_RE, _MONTH_RE, _DAY_RE])


def _parse_date_time(date_time_re: str, date_time_string: str) -> DateTime:
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


def parse_us_date_time(date_time_string: str) -> DateTime:
    """ Parse a US format date/time string of the form 'Apr 5, 2013 10:04:10 AM'. """
    return _parse_date_time(_US_DATE_TIME_RE, date_time_string)


def parse_iso_date(date_string: str) -> DateTime:
    """ Parse an ISO format date string of the form '2013-11-05'. """
    match = re.search(_ISO_DATE_RE, date_string)
    if match is None:
        raise ValueError("date_string {s!r} not matched".format(s=date_string))

    year = int(match.group('year'))
    month = int(match.group('month'))
    day = int(match.group('day'))

    return datetime.datetime(year, month, day)


def parse_iso_datetime(datetime_string: str) -> DateTime:
    """ Parse an ISO format date time string of the form '2015-10-06T15:00:01Z'. """
    return datetime.datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%SZ')


def parse_sql_datetime(datetime_string: str) -> DateTime:
    """ Parse an ISO format date time string of the form '2015-10-06T15:00:01Z'. """
    return datetime.datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S')


def percentage(numerator: Number, denominator: Number, zero_divided_by_zero_is_zero: bool = False) -> int:
    """ Return numerator / denominator * 100. """
    if float(denominator) == 0.0:
        return 0 if float(numerator) == 0.0 and zero_divided_by_zero_is_zero else 100
    return int(round((float(numerator) / float(denominator)) * 100))


def format_date(date_time: DateTime, year: int = None) -> str:
    """ Return a (Dutch) formatted version of the datetime. """
    if date_time:
        formatted_date = '{day} {month}'.format(day=date_time.day, month=MONTHS[date_time.month])
        if year:
            formatted_date += ' {year}'.format(year=date_time.year)
    else:
        formatted_date = 'onbekende datum'
    return formatted_date


def format_timedelta(timedelta: TimeDelta) -> str:
    """ Return a (Dutch) formatted version of the timedelta. """

    days = timedelta.days
    hours = timedelta.seconds // 3600
    minutes = (timedelta.seconds % 3600) // 60

    for unit, unit_singular, unit_plural in (days, 'dag', 'dagen'), (hours, 'uur', 'uur'), \
                                            (minutes, 'minuut', 'minuten'):
        if unit:
            return '{0} {1}'.format(unit, unit_plural) if unit > 1 else 'een {0}'.format(unit_singular)
    return 'minder dan een minuut'


def html_escape(text: str) -> str:
    """ Return the text with all HTML characters escaped. """
    for character, html_code in [('&', '&amp;'), ('"', '&quot;'), ("'", '&#39;'), (">", '&gt;'), ("<", '&lt;')]:
        text = text.replace(character, html_code)
    return text


def eval_json(json_string: Union[str, bytes]) -> Any:
    """ Return an evaluated version of the json string. """
    if isinstance(json_string, bytes):
        try:
            json_string = json_string.decode('utf-8')
        except UnicodeDecodeError as reason:
            logging.error("Couldn't decode %s using utf-8: %s", json_string, reason)
            raise
    try:
        return json.loads(json_string)
    except ValueError as reason:
        logging.error("Couldn't load json string '%s': %s", json_string, reason)
        raise


def version_number_to_numerical(version_number_tuple: Tuple[int, ...]) -> int:
    """ Transform the first three parts (major, minor, patch) of the version number into a numerical value.
        We assume each part is not larger than 100, so that 10000 * major + 100 * minor + patch results in a number
        for which holds that numerical_value(a.b.c.) > numerical_value(d.e.f) iff a.b.c > d.e.f. """
    result = 0
    for part, factor in zip(version_number_tuple[:3], (10000, 100, 1)):
        result += part * factor
    return result


def format_unit(unit: str) -> str:
    """ Add a space before the unit if necessary, e.g. 'LOC' -> ' LOC', but '%' -> '%'. """
    return ' ' + unit if unit and unit != '%' and not unit.startswith(' ') else unit


def url_join(*parts: str) -> str:
    """ Join the different url parts with forward slashes. """
    return "/".join([part.strip("/") for part in parts]) + ("/" if parts and parts[-1].endswith("/") else "")


def format_link_object(url: str, text: str) -> dict:
    """ Formats link dictionary object. """
    return {"href": url, "text": text}
