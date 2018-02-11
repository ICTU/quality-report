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

import datetime
import json
import unittest
import urllib
from unittest.mock import patch

from hqlib.metric_source import url_opener, FileWithDate


class UrlOpenerPrerequisitesTestCase(unittest.TestCase):
    """" Prerequisites tests for FileWithDateTestCase"""

    def test_url_opener(self):
        """" Checks if the UrlOpener, that is mocked in the tests, fulfill requirements """

        opener = url_opener.UrlOpener()

        self.assertTrue(opener is not None)
        self.assertTrue(callable(getattr(opener, "url_read", None)))


@patch.object(url_opener.UrlOpener, 'url_read')
class FileWithDateTestCase(unittest.TestCase):
    """ Unit tests for file with date metric source. """

    def test_get_iso_date_json(self, url_read_mock):
        """ Test that file with ISO date in the json format returns the correct date. """

        fake_url = 'http://fake_url'
        expected_date = datetime.datetime.now()
        url_read_mock.return_value = json.dumps({"date": expected_date.isoformat()})
        file_with_date = FileWithDate()

        result = file_with_date.get_datetime_from_content(fake_url)

        url_read_mock.assert_called_once_with(fake_url)
        self.assertEqual(expected_date, result)

    def test_get_iso_date(self, url_read_mock):
        """ Test that file with just ISO date returns the correct date. """

        fake_url = 'http://fake_url'
        expected_date = datetime.datetime.now()
        url_read_mock.return_value = expected_date.isoformat()
        file_with_date = FileWithDate()

        result = file_with_date.get_datetime_from_content(fake_url)

        url_read_mock.assert_called_once_with(fake_url)
        self.assertEqual(expected_date, result)

    def test_get_iso_date_throws(self, url_read_mock):
        """ Test that file with ISO date returns the min date when url opener throws. """

        fake_url = 'http://fake_url'
        url_read_mock.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        file_with_date = FileWithDate()

        result = file_with_date.get_datetime_from_content(fake_url)

        url_read_mock.assert_called_once_with(fake_url)
        self.assertEqual(datetime.datetime.min, result)

    def test_get_iso_date_json_throws(self, url_read_mock):
        """ Test that file with ISO date returns the min date when json loader opener throws. """

        fake_url = 'http://fake_url'
        url_read_mock.return_value = "{date:X:" + datetime.datetime.now().isoformat() + "}"
        file_with_date = FileWithDate()

        result = file_with_date.get_datetime_from_content(fake_url)

        self.assertTrue(url_read_mock.assert_called_once)
        self.assertEqual(datetime.datetime.min, result)

    def test_get_invalid_iso_date_json_throws(self, url_read_mock):
        """ Test that file with invalid ISO date in json format returns the min date."""

        fake_url = 'http://fake_url'
        url_read_mock.return_value = '{"date":"2008-13-32T00:42:18.000"}'
        file_with_date = FileWithDate()

        result = file_with_date.get_datetime_from_content(fake_url)

        url_read_mock.assert_called_once_with(fake_url)
        self.assertEqual(datetime.datetime.min, result)

    def test_get_iso_date_throws_unhandled(self, url_read_mock):
        """ Test that file with ISO date returns the min date when url opener throws. """

        fake_url = 'http://fake_url'
        url_read_mock.side_effect = Exception()
        file_with_date = FileWithDate()

        self.assertRaises(Exception, lambda: file_with_date.get_datetime_from_content(fake_url))
        url_read_mock.assert_called_once_with(fake_url)
