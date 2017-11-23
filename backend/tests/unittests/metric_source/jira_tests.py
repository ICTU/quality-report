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

from hqlib.metric_source import Jira


class JiraUnderTest(Jira):  # pylint: disable=too-few-public-methods
    """ Override class to return a fixed JSON file. """

    issues = '[]'

    def url_read(self, url):  # pylint: disable=unused-argument
        """ Return the static content. """
        if 'raise' in url:
            raise urllib.error.HTTPError(None, None, None, None, None)
        else:
            return '{{"searchUrl": "http://search", "viewUrl": "http://view", "total": 5, "issues": {0}}}'.format(
                self.issues)


class JiraTest(unittest.TestCase):
    """ Unit tests for the Jira class. """

    def setUp(self):
        self.__jira = JiraUnderTest('http://jira/', 'username', 'password')

    def test_query_total(self):
        """ Test that the correct number of issues is returned. """
        self.assertEqual(5, self.__jira.query_total('12345'))

    def test_query_total_without_query(self):
        """ Test that the result is -1 when no query id is passed. """
        self.assertEqual(-1, self.__jira.query_total(''))

    def test_query_sum(self):
        """ Test that the total number of minutes spend on manual test cases is correct. """
        self.__jira.issues = '[{"fields": {"customfield_11700": "20"}},' \
                             ' {"fields": {"customfield_11700": 100}},' \
                             ' {"fields": {"customfield_11700": null}}]'
        self.assertEqual(120, self.__jira.query_sum('12345', 'customfield_11700'))

    def test_query_sum_without_query(self):
        """ Test that the manual test time is -1 when Jira has no query id. """
        self.assertEqual(-1, self.__jira.query_sum('', ''))

    def test_query_field_empty(self):
        """ Test that the number of issues with empty field is correct. """
        self.__jira.issues = '[{"fields": {"customfield_11700": "20"}},' \
                             ' {"fields": {"customfield_11700": 100}},' \
                             ' {"fields": {"customfield_11700": null}}]'
        self.assertEqual(1, self.__jira.query_field_empty('filter id', 'customfield_11700'))

    def test_nr_manual_tests_not_measured_without_query(self):
        """ Test that the number of issues is -1 when Jira has no query id. """
        self.assertEqual(-1, self.__jira.query_field_empty('', ''))

    def test_get_query_url(self):
        """ Test that the url is correct. """
        self.assertEqual("http://search", self.__jira.get_query_url('filter id'))

    def test_get_query_url_view(self):
        """ Test that the url is correct. """
        self.assertEqual("http://view", self.__jira.get_query_url('filter id', search=False))


class JiraWhenFailingTest(unittest.TestCase):
    """ Unit tests for a Jira that's unavailable. """

    def setUp(self):
        self.__jira = JiraUnderTest('http://raise', 'username', 'password')

    def test_query_total(self):
        """ Test that the query total is -1 when Jira is not available. """
        self.assertEqual(-1, self.__jira.query_total('filter id'))

    def test_query_sum(self):
        """ Test that the query sum is -1 when Jira is not available. """
        self.assertEqual(-1, self.__jira.query_sum('filter id', 'field'))

    def testquery_field_empty(self):
        """ Test that the query_field_empty return -1 when Jira is not available. """
        self.assertEqual(-1, self.__jira.query_field_empty('filter id', 'field'))
