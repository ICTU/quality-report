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

import unittest
from unittest.mock import patch
import urllib.error
from hqlib.metric_source import Jira, url_opener


@patch.object(url_opener.UrlOpener, '__init__')
class JiraConstructorTests(unittest.TestCase):
    """ Unit tests of the constructor of the Jira class. """

    def test_url_opener_constructor(self, init_mock):
        """ Test that by Jira initialisation, UrlOpener is initialised with user name and password as parameters. """
        init_mock.return_value = None

        Jira('http://jira/', 'jira_username', 'jira_password')

        init_mock.assert_called_with(username='jira_username', password='jira_password')

    def test_url_is_padded(self, init_mock):
        """ Tests that jira url is padded if needed."""
        init_mock.return_value = None

        jira = Jira('X', '', '')

        self.assertEqual('X/', jira._Jira__url)

    def test_url_padding(self, init_mock):
        """ Tests that jira url is not padded if not needed."""
        init_mock.return_value = None

        jira = Jira('X/', '', '')

        self.assertEqual('X/', jira._Jira__url)


@patch.object(url_opener.UrlOpener, 'url_read')
class JiraTest(unittest.TestCase):
    """ Unit tests for the Jira class. """

    def test_get_issue_details(self, url_read_mock):
        """ Test that the issue details are correctly retrieved. """
        jira = Jira('http://jira/', '', '')
        url_read_mock.return_value = '{"x": "1"}'

        result = jira.get_issue_details('ISS-ID')

        url_read_mock.assert_called_once_with(
            'http://jira/rest/api/2/issue/ISS-ID?expand=changelog&fields="*all,-comment"'
        )
        self.assertEqual({"x": "1"}, result)

    def test_get_issue_details_http_error(self, url_read_mock):
        """ Test that the issue details are None when hrrp error occurs. """
        jira = Jira('http://jira/', '', '')
        url_read_mock.side_effect = urllib.error.HTTPError(None, None, None, None, None)

        result = jira.get_issue_details('ISS-ID')

        url_read_mock.assert_called_once_with(
            'http://jira/rest/api/2/issue/ISS-ID?expand=changelog&fields="*all,-comment"'
        )
        self.assertEqual(None, result)

    def test_get_issue_details_json_error(self, url_read_mock):
        """ Test that the issue details are None when json is incorrect . """
        jira = Jira('http://jira/', '', '')
        url_read_mock.return_value = 'not json'

        result = jira.get_issue_details('ISS-ID')

        url_read_mock.assert_called_once_with(
            'http://jira/rest/api/2/issue/ISS-ID?expand=changelog&fields="*all,-comment"'
        )
        self.assertEqual(None, result)

    def test_get_query_url_view(self, url_read_mock):
        """ Test that the view url is correctly retrieved. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.return_value = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'

        result = jira.get_query_url('filter id', search=False)

        url_read_mock.assert_called_once_with('http://jira/rest/api/2/filter/filter id')
        self.assertEqual("http://jira/view", result)

    def test_get_query_url_search(self, url_read_mock):
        """ Test that the search url is correctly retrieved. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.return_value = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'

        result = jira.get_query_url('filter id', search=True)

        url_read_mock.assert_called_once_with('http://jira/rest/api/2/filter/filter id')
        self.assertEqual("http://jira/search", result)

    def test_get_query_url_empty_id(self, url_read_mock):
        """ Test that the url is None when empty metric source id is given. """
        jira = Jira('http://jira/', '', '')

        result = jira.get_query_url('')

        url_read_mock.assert_not_called()
        self.assertEqual(None, result)

    def test_get_query_url_http_error(self, url_read_mock):
        """ Test that the url is None when http error occurs. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.side_effect = urllib.error.HTTPError(None, None, None, None, None)

        result = jira.get_query_url('filter id')

        url_read_mock.assert_called_once_with('http://jira/rest/api/2/filter/filter id')
        self.assertEqual(None, result)

    @patch.object(Jira, 'get_query_url')
    def test_get_query(self, get_query_url_mock, url_read_mock):
        """ Test that the query is correctly retrieved. """
        jira = Jira('http://jira/', '', '')
        get_query_url_mock.return_value = "http://other/what?that=1"
        url_read_mock.return_value = '{"x": "y"}'

        result = jira.get_query('filter id')

        get_query_url_mock.assert_called_once()
        url_read_mock.assert_called_once_with('http://jira/what?that=1')
        self.assertEqual({"x": "y"}, result)

    @patch.object(Jira, 'get_query_url')
    def test_get_query_query_url_empty(self, get_query_url_mock, url_read_mock):
        """ Test that the query result is None when query url returns empty result. """
        jira = Jira('http://jira/', '', '')
        get_query_url_mock.return_value = ""

        result = jira.get_query('filter id')

        get_query_url_mock.assert_called_once()
        url_read_mock.assert_not_called()
        self.assertEqual(None, result)

    @patch.object(Jira, 'get_query_url')
    def test_get_query_http_error(self, get_query_url_mock, url_read_mock):
        """  Test that the query result is None when http error occurs. """
        jira = Jira('http://jira/', '', '')
        get_query_url_mock.return_value = "http://other/what?that=1"
        url_read_mock.side_effect = urllib.error.HTTPError(None, None, None, None, None)

        result = jira.get_query('filter id')

        get_query_url_mock.assert_called_once()
        url_read_mock.assert_called_once_with('http://jira/what?that=1')
        self.assertEqual(None, result)
