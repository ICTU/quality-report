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

import datetime
import unittest

from hqlib import utils


class PercentageTest(unittest.TestCase):
    """ Unit tests of the percentage method. """
    def test_some_values(self):
        """Test some random values. """
        self.assertEqual(50, utils.percentage(25, 50))
        self.assertEqual(200, utils.percentage(50, 25))
        self.assertEqual(100, utils.percentage(.5, .5))

    def test_denominator_zero(self):
        """ Test that percentage is 100 when denominator is zero. """
        self.assertEqual(100, utils.percentage(100, 0))

    def test_numerator_zero(self):
        """ Test that percentage is 0 when numerator is zero. """
        self.assertEqual(0, utils.percentage(0, 100))

    def test_zero_division(self):
        """ Test that percentage is 0 when denominator is zero. """
        self.assertEqual(100, utils.percentage(0, 0))

    def test_zero_devision_is_zero(self):
        """ Test that percentage is 0 when denominator is zero. """
        self.assertEqual(0, utils.percentage(0, 0, zero_divided_by_zero_is_zero=True))


class WorkdaysInPeriodTest(unittest.TestCase):
    """ Unit tests of the workdays in period method. """
    def assert_period(self, period_length, period_start, period_end):
        """ Helper method for checking the length of a period. """
        self.assertEqual(period_length,
                         utils.workdays_in_period(datetime.date(*period_start), datetime.date(*period_end)))

    def test_monday_wednesday(self):
        """ Test that a period from Monday to Wednesday is 3 work days. """
        self.assert_period(3, (2012, 12, 17), (2012, 12, 19))

    def test_one_day(self):
        """ Test that a period with start date equal to end date is 1 work
            day. """
        self.assert_period(1, (2012, 12, 17), (2012, 12, 17))

    def test_weekend_in_period(self):
        """ Test that a weekend inside the period is not counted. """
        self.assert_period(2, (2012, 12, 14), (2012, 12, 17))

    def test_period_in_weekend(self):
        """ Test that the number of work days is zero when the period starts
            and ends in the same weekend. """
        self.assert_period(0, (2012, 12, 15), (2012, 12, 16))

    def test_start_in_weekend(self):
        """ Test that a weekend is not counted when the start is in the
            weekend. """
        self.assert_period(1, (2012, 12, 16), (2012, 12, 17))

    def test_end_in_weekend(self):
        """ Test that a weekend is not counted when the start is in the
            weekend. """
        self.assert_period(5, (2012, 12, 17), (2012, 12, 23))


class FormatDateTest(unittest.TestCase):
    """ Unit tests of the format date method. """
    def test_some_date(self):
        """ Test that a date time is formatted as a day and month. """
        self.assertEqual('19 december', utils.format_date(datetime.datetime(2012, 12, 19)))

    def test_missing_date(self):
        """ Test that None is formatted as missing date. """
        self.assertEqual('onbekende datum', utils.format_date(None))

    def test_date_with_year(self):
        """ Test that a date time can be formatted with the year included. """
        self.assertEqual('19 december 2012',
                         utils.format_date(datetime.datetime(2012, 12, 19), year=True))


class FormatTimeDeltaTest(unittest.TestCase):
    """ Unit tests of the format time delta method. """
    def assert_format(self, formatted_time_delta, **time_delta_args):
        """ Check that the time delta is formatted correctly. """
        self.assertEqual(formatted_time_delta, utils.format_timedelta(datetime.timedelta(**time_delta_args)))

    def test_one_second(self):
        """ Test that less than a minute is formatted as one minute. """
        self.assert_format('minder dan een minuut', seconds=1)

    def test_one_minute(self):
        """ Test that exactly one minute doesn't include seconds. """
        self.assert_format('een minuut', minutes=1)

    def test_two_minutes(self):
        """ Test that two minutes is formatted correctly. """
        self.assert_format('2 minuten', minutes=2)

    def test_one_hour(self):
        """ Test that exactly one hour doesn't include minutes. """
        self.assert_format('een uur', hours=1)

    def test_one_and_a_half_hour(self):
        """ Test that one and a half hour doesn't include minutes. """
        self.assert_format('een uur', hours=1.5)

    def test_three_and_a_half_hour(self):
        """ Test that more than three hours doesn't include minutes. """
        self.assert_format('3 uur', hours=3.5)

    def test_one_day(self):
        """ Test that one day is formatted as one day. """
        self.assert_format('een dag', days=1)

    def test_one_day_and_one_hour(self):
        """ Test that one day and one hour doesn't include the hours. """
        self.assert_format('een dag', hours=25)

    def test_two_days(self):
        """ Test that two days is formatted as 2 days. """
        self.assert_format('2 dagen', hours=48)

    def test_two_days_and_a_few_hours(self):
        """ Test that two days doesn't include hours. """
        self.assert_format('2 dagen', hours=55)


class HtmlEscapeTest(unittest.TestCase):
    """ Unit tests of the HTML escape method. """
    def test_empty_string(self):
        """ Test that an empty string works. """
        self.assertEqual('', utils.html_escape(''))

    def test_ampersand(self):
        """ Test that an ampersand is escaped correctly. """
        self.assertEqual('a&amp;b', utils.html_escape('a&b'))

    def test_double_quote(self):
        """ Test that double quotes are escaped correctly. """
        self.assertEqual('&quot;quoted&quot;', utils.html_escape('"quoted"'))

    def test_single_quote(self):
        """ Test that single quotes are escaped correctly. """
        self.assertEqual('&#39;quoted&#39;', utils.html_escape("'quoted'"))

    def test_tag(self):
        """ Test that tags are escaped correctly. """
        self.assertEqual('&lt;tag&gt;', utils.html_escape('<tag>'))


class EvalJSONTest(unittest.TestCase):
    """ Unit tests for the json evaluation method. """
    def test_empty_json(self):
        """ Test that an empty JSON dict results in a Python dict. """
        self.assertEqual(dict(), utils.eval_json('{}'))

    def test_eval_true(self):
        """ Test that 'true' is evaluated. """
        self.assertEqual(dict(bla=True), utils.eval_json('{"bla": true}'))

    def test_eval_false(self):
        """ Test that 'false' is evaluated. """
        self.assertEqual(dict(bla=False), utils.eval_json('{"bla" : false}'))

    def test_eval_null(self):
        """ Test that 'null' is evaluated. """
        self.assertEqual(dict(bla=None), utils.eval_json('{"bla": null}'))

    def test_eval_decimal(self):
        """ Test that a decimal number is evaluated. """
        self.assertEqual(dict(bla=1), utils.eval_json('{"bla": 1}'))

    def test_eval_float(self):
        """ Test that a float number is evaluated. """
        self.assertEqual(dict(bla=1.5), utils.eval_json('{"bla": 1.5}'))

    def test_decode_bytes(self):
        """ Test that bytes are first decoded. """
        self.assertEqual(dict(bla=1), utils.eval_json(b'{"bla": 1}'))

    def test_unicode_decode_error(self):
        """ Test that a unicode decode error is raised when the bytes can't be decoded using utf-8. """
        self.assertRaises(UnicodeDecodeError, utils.eval_json, b'\x80abc')

    def test_value_error(self):
        """ Test that a value error is raised when evaluating incompletw json. """
        self.assertRaises(ValueError, utils.eval_json, '{')


class ParseUSDateTimeTest(unittest.TestCase):
    """ Unit tests for the parse US date time method. """
    def test_am(self):
        """ Test that parsing an AM time works. """
        self.assertEqual(datetime.datetime(2013, 4, 5, 10, 0, 0), utils.parse_us_date_time('Apr 5, 2013 10:00:00 AM'))

    def test_pm(self):
        """ Test that parsing a PM time works. """
        self.assertEqual(datetime.datetime(2013, 4, 5, 22, 0, 0), utils.parse_us_date_time('Apr 5, 2013 10:00:00 PM'))

    def test_12pm(self):
        """ Test that parsing 12 PM works. """
        self.assertEqual(datetime.datetime(2013, 4, 9, 12, 2, 43), utils.parse_us_date_time('Apr 9, 2013 12:02:43 PM'))

    def test_non_string(self):
        """ Test that parsing a non-string throws an exception. """
        self.assertRaises(TypeError, utils.parse_us_date_time, None)

    def test_invalid(self):
        """ Test that parsing an invalid string throws an exception. """
        self.assertRaises(ValueError, utils.parse_us_date_time, 'Apr -1')


class ParseISODateTest(unittest.TestCase):
    """ Unit tests for the parse ISO date method. """
    def test_some_date(self):
        """ Test that parsing a random date works. """
        self.assertEqual(datetime.datetime(2013, 11, 5), utils.parse_iso_date('2013-11-05'))

    def test_invalid(self):
        """ Test that parsing an invalid string throws an exception. """
        self.assertRaises(ValueError, utils.parse_iso_date, 'Apr -1')


class ParseISODateTimeTest(unittest.TestCase):
    """ Unit tests for the parse ISO date time method. """
    def test_some_datetime(self):
        """ Test that parsing a random date time works. """
        self.assertEqual(datetime.datetime(2015, 10, 6, 15, 0, 1), utils.parse_iso_datetime('2015-10-06T15:00:01Z'))

    def test_invalid(self):
        """ Test that parsing an invalid string throws an exception. """
        self.assertRaises(ValueError, utils.parse_iso_datetime, 'Apr -1')


class VersionNumberToNumericalTest(unittest.TestCase):
    """ Unit tests for the version number to numerical conversion method. """
    def test_version_number(self):
        """ Test a regular version number. """
        self.assertEqual(10203, utils.version_number_to_numerical((1, 2, 3)))

    def test_long_version_number(self):
        """ Test a long version number. """
        self.assertEqual(10203, utils.version_number_to_numerical((1, 2, 3, 4)))

    def test_short_version_number(self):
        """ Test a short version number. """
        self.assertEqual(10200, utils.version_number_to_numerical((1, 2)))
