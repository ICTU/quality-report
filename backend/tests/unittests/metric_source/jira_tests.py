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

import unittest
import urllib.error

from unittest.mock import patch, call
from hqlib.metric_source import Jira, url_opener

@patch.object(url_opener.UrlOpener, '__init__')
class JiraCostructorTests(unittest.TestCase):
    """ Unit tests of the constructor of the Jira class. """

    def test_url_opener_constructor(self, init_mock):
        """" Test that by Jira initialisation, UrlOpener is initialised with user name and password as parameters. """
        init_mock.return_value = None

        Jira('http://jira/', 'jira_username', 'jira_password')

        init_mock.assert_called_with(username='jira_username', password='jira_password')

    def test_url_is_padded(self, init_mock):
        """" Tests that jira url is padded if needed."""
        init_mock.return_value = None

        jira = Jira('X', '', '')

        self.assertEqual('X/', jira._Jira__url)

    def test_url_padding(self, init_mock):
        """" Tests that jira url is not padded if not needed."""
        init_mock.return_value = None

        jira = Jira('X/', '', '')

        self.assertEqual('X/', jira._Jira__url)


@patch.object(url_opener.UrlOpener, 'url_read')
class JiraTest(unittest.TestCase):
    """ Unit tests for the Jira class. """

    def test_query_total(self, url_read_mock):
        """ Test that the correct number of issues is returned. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.side_effect = ['{"searchUrl":"http://jira/search?filter_criteria"}',
            '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}']

        result = jira.query_total('12345')

        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/12345'),
            call('http://jira/search?filter_criteria')])
        self.assertEqual(5, result)

    def test_query_total_without_query(self, url_read_mock):
        """ Test that the result is -1 when no query id is passed. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.return_value = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'

        result = jira.query_total('')

        url_read_mock.assert_not_called()
        self.assertEqual(-1, result)

    def test_query_sum(self, url_read_mock):
        """ Test that the total number of minutes spend on manual test cases is correct. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.return_value = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5", ' \
                                     '"issues": [{"fields": {"customfield_11700": "20"}}, ' \
                                     '{"fields": {"customfield_11700": 100}}, {"fields": {"customfield_11700": null}}]}'

        result = jira.query_sum('12345', 'customfield_11700')

        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/12345'),
            call('http://jira/search?')])
        self.assertEqual(120, result)

    def test_query_sum_without_query(self, url_read_mock):
        """ Test that the manual test time is -1 when Jira has no query id. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.return_value = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5",' \
                                     ' "issues": []}'

        result = jira.query_sum('', '')

        url_read_mock.assert_not_called()
        self.assertEqual(-1, result)

    def test_query_field_empty(self, url_read_mock):
        """ Test that the number of issues with empty field is correct. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.return_value = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5", ' \
                                     '"issues": [{"fields": {"customfield_11700": "20"}}, ' \
                                     '{"fields": {"customfield_11700": 100}}, {"fields": {"customfield_11700": null}}]}'

        result = jira.query_field_empty('filter id', 'customfield_11700')

        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/filter id'),
            call('http://jira/search?')])
        self.assertEqual(1, result)

    def test_nr_manual_tests_not_measured_without_query(self, url_read_mock):
        """ Test that the number of issues is -1 when Jira has no query id. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.return_value = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'

        result = jira.query_field_empty('', '')

        url_read_mock.assert_not_called()
        self.assertEqual(-1, result)

    def test_get_query_url_view(self, url_read_mock):
        """ Test that the url is correct. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.return_value = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'

        result = jira.get_query_url('filter id', search=False)

        url_read_mock.assert_called_once_with('http://jira/rest/api/2/filter/filter id')
        self.assertEqual("http://jira/view", result)

    def test_get_query_url_search(self, url_read_mock):
        """ Test that the url is correct. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.return_value = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'

        result = jira.get_query_url('filter id', search=True)

        url_read_mock.assert_called_once_with('http://jira/rest/api/2/filter/filter id')
        self.assertEqual("http://jira/search", result)


@patch.object(url_opener.UrlOpener, 'url_read')
class JiraWhenFailingTest(unittest.TestCase):
    """ Unit tests for a Jira that's unavailable. """

    def test_query_total(self, url_read_mock):
        """ Test that the query total is -1 when Jira is not available. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.side_effect = urllib.error.HTTPError(None, None, None, None, None)

        result = jira.query_total('filter id')

        url_read_mock.assert_called_once_with('http://jira/rest/api/2/filter/filter id')
        self.assertEqual(-1, result)

    def test_query_sum(self, url_read_mock):
        """ Test that the query sum is -1 when Jira is not available. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.side_effect = urllib.error.HTTPError(None, None, None, None, None)

        result = jira.query_sum('filter id', 'field')

        url_read_mock.assert_called_once_with('http://jira/rest/api/2/filter/filter id')
        self.assertEqual(-1, result)

    def testquery_field_empty(self, url_read_mock):
        """ Test that the query_field_empty return -1 when Jira is not available. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.side_effect = urllib.error.HTTPError(None, None, None, None, None)

        result = jira.query_field_empty('filter id', 'field')

        url_read_mock.assert_called_once_with('http://jira/rest/api/2/filter/filter id')
        self.assertEqual(-1, result)
