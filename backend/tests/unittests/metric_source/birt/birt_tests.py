"""
Copyright 2012-2019 Ministerie van Sociale Zaken en Werkgelegenheid

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

import logging
import unittest
from unittest.mock import patch
import datetime
import pathlib
import urllib.error

from hqlib.metric_source import Birt, url_opener


def read_html(filename: str) -> str:
    """ Read the html file and return its contents. """
    return (pathlib.Path(__file__).resolve().parent / filename).read_text()


TEST_DESIGN_HTML = read_html("test_design.html")
MANUAL_TEST_EXECUTION_HTML = read_html("manual_test_execution.html")
MANUAL_TEST_EXECUTION_HTML_NEVER_EXECUTED = read_html("manual_test_execution_never_executed.html")


class BirtTestUrls(unittest.TestCase):
    """ Unit tests for urls of the Birt class. """

    def test_url(self):
        """ Test the url. """
        self.assertEqual('http://birt/birt/', Birt('http://birt/').url())

    def test_test_design_url(self):
        """ Test the test design url. """
        self.assertEqual('http://birt/birt/preview?__report=reports/test_design.rptdesign',
                         Birt('http://birt/').test_design_url())

    def test_whats_missing_url(self):
        """ Test the what's missing report url. """
        self.assertEqual('http://birt/birt/preview?__report=reports/whats_missing.rptdesign',
                         Birt('http://birt/').whats_missing_url())

    def test_metric_source_urls(self):
        """ Test the what's missing report url. """
        self.assertEqual(['http://birt/birt/preview?__report=reports/whats_missing.rptdesign'],
                         Birt('http://birt/').metric_source_urls())

    def test_manual_test_url_trunk(self):
        """ Test the manual test execution url for the trunk. """
        self.assertEqual(
            'http://birt/birt/preview?__report=reports/manual_test_execution_report.rptdesign&version=trunk',
            Birt('http://birt/').manual_test_execution_url())

    def test_manual_test_url_version(self):
        """ Test the manual test execution url with a specific version. """
        self.assertEqual('http://birt/birt/preview?__report=reports/manual_test_execution_report.rptdesign&version=1',
                         Birt('http://birt/').manual_test_execution_url('1'))


@patch.object(url_opener.UrlOpener, 'url_open')
class BirtTest(unittest.TestCase):
    """ Unit tests for the Birt class. """

    # pylint: disable=too-many-public-methods

    def setUp(self):
        self.__birt = Birt('http://birt/')

    def test_nr_user_stories_with_sufficient_ltcs(self, mock_url_open):
        """ Test that the number of user stories with sufficient number of logical test cases is correct. """
        mock_url_open.return_value = TEST_DESIGN_HTML
        self.assertEqual((22, []), self.__birt.nr_user_stories_with_sufficient_ltcs())

    @patch.object(logging, 'warning')
    def test_nr_user_stories_with_sufficient_ltcs_on_error(self, mock_warning, mock_url_open):
        """ Test that the number of user stories is -1 when Birt is unavailable. """
        mock_url_open.side_effect = urllib.error.URLError('Birt down')
        self.assertEqual((-1, []), self.__birt.nr_user_stories_with_sufficient_ltcs())
        mock_warning.assert_called_once()

    def test_nr_automated_ltcs(self, mock_url_open):
        """ Test the number of automated logical test cases is correct. """
        mock_url_open.return_value = TEST_DESIGN_HTML
        self.assertEqual((111, []), self.__birt.nr_automated_ltcs())

    @patch.object(logging, 'warning')
    def test_nr_automated_ltcs_on_error(self, mock_warning, mock_url_open):
        """ Test that the number of automated logical test cases is -1 when Birt is unavailable. """
        mock_url_open.side_effect = urllib.error.URLError('Birt down')
        self.assertEqual((-1, []), self.__birt.nr_automated_ltcs())
        mock_warning.assert_called_once()

    def test_nr_user_stories(self, mock_url_open):
        """ Test that the number of user stories is correct. """
        mock_url_open.return_value = TEST_DESIGN_HTML
        self.assertEqual((23, []), self.__birt.nr_user_stories())

    def test_reviewed_user_stories(self, mock_url_open):
        """ Test that the number of reviewed user stories is correct. """
        mock_url_open.return_value = TEST_DESIGN_HTML
        self.assertEqual((23, []), self.__birt.reviewed_user_stories())

    def test_approved_user_stories(self, mock_url_open):
        """ Test that the number of approved user stories is correct. """
        mock_url_open.return_value = TEST_DESIGN_HTML
        self.assertEqual((23, []), self.__birt.approved_user_stories())

    def test_not_approved_user_stories(self, mock_url_open):
        """ Test that the number of not approved user stories is correct. """
        mock_url_open.return_value = TEST_DESIGN_HTML
        self.assertEqual(0, self.__birt.not_approved_user_stories())

    def test_nr_ltcs(self, mock_url_open):
        """ Test that the number of logical test cases is correct. """
        mock_url_open.return_value = TEST_DESIGN_HTML
        self.assertEqual((182, []), self.__birt.nr_ltcs())

    def test_reviewed_ltcs(self, mock_url_open):
        """ Test that the number of reviewed logical test cases is correct. """
        mock_url_open.return_value = TEST_DESIGN_HTML
        self.assertEqual((182, []), self.__birt.reviewed_ltcs())

    def test_approved_ltcs(self, mock_url_open):
        """ Test that the number of approved logical test cases is correct. """
        mock_url_open.return_value = TEST_DESIGN_HTML
        self.assertEqual((182, []), self.__birt.approved_ltcs())

    def test_not_approved_ltcs(self, mock_url_open):
        """ Test that the number of not approved logical test cases is correct. """
        mock_url_open.return_value = TEST_DESIGN_HTML
        self.assertEqual(0, self.__birt.not_approved_ltcs())

    def test_nr_ltcs_to_be_automated(self, mock_url_open):
        """ Test that the number of logical test cases to be automated is correct. """
        mock_url_open.return_value = TEST_DESIGN_HTML
        self.assertEqual((165, []), self.__birt.nr_ltcs_to_be_automated())

    def test_nr_manual_ltcs(self, mock_url_open):
        """ Test that the number of manual logical test cases is correct. """
        mock_url_open.return_value = MANUAL_TEST_EXECUTION_HTML
        self.assertEqual((3, []), self.__birt.nr_manual_ltcs('bulk'))

    @patch.object(logging, 'warning')
    def test_nr_manual_ltcs_on_error(self, mock_warning, mock_url_open):
        """ Test that the number of manual logical test cases is -1 when Birt is not available. """
        mock_url_open.side_effect = urllib.error.URLError('Birt down')
        self.assertEqual((-1, []), self.__birt.nr_manual_ltcs('bulk'))
        mock_warning.assert_called_once()

    def test_nr_manual_ltcs_too_old(self, mock_url_open):
        """ Test that the number of manual logical test cases that have not been tested recently is correct. """
        mock_url_open.return_value = MANUAL_TEST_EXECUTION_HTML
        self.assertEqual(3, self.__birt.nr_manual_ltcs_too_old('trunk', 7))

    @patch.object(logging, 'warning')
    def test_nr_manual_ltcs_too_old_on_error(self, mock_warning, mock_url_open):
        """ Test that the number of manual logical test cases is -1 whe Birt is not available. """
        mock_url_open.side_effect = urllib.error.URLError('Birt down')
        self.assertEqual(-1, self.__birt.nr_manual_ltcs_too_old('trunk', 7))
        mock_warning.assert_called_once()

    def test_no_date_manual_tests(self, mock_url_open):
        """ Test that the date of the last manual test execution is correct. """
        mock_url_open.return_value = MANUAL_TEST_EXECUTION_HTML_NEVER_EXECUTED
        date = self.__birt.date_of_last_manual_test()
        self.assertEqual(datetime.datetime(2015, 8, 4), date)

    def test_late_date_manual_tests(self, mock_url_open):
        """ Test that the date of the last manual test execution is correct. """
        mock_url_open.return_value = MANUAL_TEST_EXECUTION_HTML
        date = self.__birt.date_of_last_manual_test()
        self.assertEqual(datetime.datetime(2015, 8, 19), date)

    @patch.object(logging, 'warning')
    def test_date_of_last_manual_test_on_error(self, mock_warning, mock_url_open):
        """ Test that the date of the last manual test execution is the min date when Birt is unavailable. """
        mock_url_open.side_effect = urllib.error.URLError('Birt down')
        self.assertEqual(datetime.datetime.min, self.__birt.date_of_last_manual_test())
        mock_warning.assert_called_once()
