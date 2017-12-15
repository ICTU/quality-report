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

from hqlib.metric_source import Jira, JiraFilter, url_opener
from unittest.mock import patch, call


class JiraFilterTest(unittest.TestCase):
    """ Test the Jira filter metric source. """

    @patch.object(Jira, 'query_total')
    def test_nr_issues(self, query_total_mock):
        """ Test that the number of items equals the sum of totals per metric source returned by Jira. """
        query_total_mock.side_effect = [12, 13]

        result = JiraFilter('', '', '', jira=Jira('', '', '')).nr_issues('123', '567')

        query_total_mock.assert_has_calls([call(123), call(567)])
        self.assertEqual(25, result)

    @patch.object(Jira, 'query_total')
    def test_nr_issues_on_error(self, query_total_mock):
        """ Test that the number of items is set to -1 if Jira returned -1 for any metric source. """
        query_total_mock.side_effect = [-1, 13]

        result = JiraFilter('', '', '', jira=Jira('', '', '')).nr_issues('123', '567')

        query_total_mock.assert_has_calls([call(123), call(567)])
        self.assertEqual(-1, result)

    @patch.object(Jira, 'query_sum')
    def test_sum_field(self, query_sum_mock):
        """ Test that the number of points equals the sum of sums per metric source returned by Jira. """
        query_sum_mock.side_effect = [12.1, 13.2]

        result = JiraFilter('', '', '', jira=Jira('', '', ''), field_name='customfield_1').sum_field('123', '567')

        query_sum_mock.assert_has_calls([call(123,'customfield_1'), call(567, 'customfield_1')])
        self.assertAlmostEqual(25.3, result)

    @patch.object(Jira, 'query_sum')
    def test_sum_field_on_error(self, query_sum_mock):
        """ Test that the number of points is set to -1 if Jira returned -1 for any metric source. """
        query_sum_mock.side_effect = [-1, 13.2]

        result = JiraFilter('', '', '', jira=Jira('', '', ''), field_name='customfield_1').sum_field('123', '567')

        query_sum_mock.assert_has_calls([call(123, 'customfield_1'), call(567, 'customfield_1')])
        self.assertEqual(-1, result)

    @patch.object(Jira, 'get_query_url')
    def test_url(self, get_query_url_mock):
        """ Test that the Jira filter returns the correct urls for the filters. """
        jira1 = 'http://jira1/view'
        jira2 = 'http://jira2/view'
        get_query_url_mock.side_effect = [jira1, jira2]

        result = JiraFilter('', '', '', jira=Jira('http://jira/', '', '')).metric_source_urls('123', '567')

        get_query_url_mock.assert_has_calls([call(123, search=False), call(567, search=False)])
        self.assertEqual([jira1, jira2], result)

    @patch.object(Jira, 'query_field_empty')
    def test_nr_issues_field_empty(self, query_field_empty_mock):
        """ Test that the number of points equals the sum of sums per metric source returned by Jira. """
        query_field_empty_mock.side_effect = [1, 2]

        result = JiraFilter('', '', '', jira=Jira('', '', ''), field_name='customfield_1').nr_issues_with_field_empty(
            '123', '567')

        query_field_empty_mock.assert_has_calls([call(123, 'customfield_1'), call(567, 'customfield_1')])
        self.assertEqual(3, result)

    @patch.object(Jira, 'query_field_empty')
    def test_nr_issues_field_empty_on_error(self, query_field_empty_mock):
        """ Test that the number of points is set to -1 if Jira returned -1 for any metric source. """
        query_field_empty_mock.side_effect = [-1, 2]

        result = JiraFilter('', '', '', jira=Jira('', '', ''), field_name='customfield_1').nr_issues_with_field_empty(
            '123', '567')

        query_field_empty_mock.assert_has_calls([call(123, 'customfield_1'), call(567, 'customfield_1')])
        self.assertEqual(-1, result)
