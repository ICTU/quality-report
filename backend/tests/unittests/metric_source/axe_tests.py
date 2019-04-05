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
from hqlib.metric_source import AxeReport, url_opener


AXE_CSV_GENERAL = 'URL,Violation Type,Impact,Help,HTML Element,Messages,DOM Element{new_line_char}' \
    'http://url:222/page/with/error,image-alt,critical,https://explanation,unimppoprtant,Description,dom-element'

AXE_CSV = AXE_CSV_GENERAL.format(new_line_char='\r')


class AxeReportInitTest(unittest.TestCase):
    """ Unit tests for initialisation of AxeReport class. """

    @patch.object(url_opener.UrlOpener, '__init__')
    def test_url_opener_init(self, url_opener_init__mock):
        """ Test that the url opener is initialized with the same arguments as AxeReport. """

        url_opener_init__mock.return_value = None
        axe = AxeReport(username='un', password='pwd', or_whatever_it_might_be='x')

        self.assertIsNotNone(axe)
        url_opener_init__mock.assert_called_once_with(username='un', password='pwd', or_whatever_it_might_be='x')


@patch.object(url_opener.UrlOpener, 'url_read')
class AxeReportTest(unittest.TestCase):
    """ Unit tests for AxeReport class. """

    def test_nr_violations(self, url_read_mock):
        """ Test that the number of violations is correct """
        url_read_mock.return_value = AXE_CSV
        axe = AxeReport()

        result = axe.nr_violations('url')

        self.assertEqual(result, 1)
        url_read_mock.assert_called_once_with('url')

    def test_nr_violations_with_cr(self, url_read_mock):
        """ Test that the number of violations is correct """
        url_read_mock.return_value = AXE_CSV_GENERAL.format(new_line_char='\r')
        axe = AxeReport()

        result = axe.nr_violations('url')

        self.assertEqual(result, 1)
        url_read_mock.assert_called_once_with('url')

    @patch.object(logging, 'error')
    def test_nr_violations_http_error(self, mock_error, url_read_mock):
        """ Test that the number of violations is correct """
        url_read_mock.side_effect = TimeoutError
        axe = AxeReport()

        result = axe.nr_violations('url')

        self.assertEqual(-1, result)
        mock_error.assert_called_once_with("Error retrieving accessibility report from %s.", 'url')

    def test_violations(self, url_read_mock):
        """ Test that the expected violations are returned in correct format """
        url_read_mock.return_value = AXE_CSV
        axe = AxeReport()

        result = axe.violations('url')

        self.assertEqual([
            ('critical', 'image-alt', 'https://explanation', '/page/with/error', 'dom-element', 'Description')], result)
        url_read_mock.assert_called_once_with('url')

    @patch.object(logging, 'error')
    def test_violations_http_error(self, mock_error, url_read_mock):
        """ Test that the expected violations are returned in correct format """
        url_read_mock.side_effect = TimeoutError
        axe = AxeReport()

        result = axe.violations('url')

        self.assertEqual([], result)
        mock_error.assert_called_once_with("Error retrieving accessibility report from %s.", 'url')
