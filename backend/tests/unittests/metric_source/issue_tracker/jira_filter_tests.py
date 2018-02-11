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
from unittest.mock import patch, call

from hqlib.metric_source import Jira, JiraFilter
from hqlib.domain import ExtraInfo


class JiraFilterTest(unittest.TestCase):
    """ Test the Jira filter metric source. """

    @patch.object(Jira, 'query_total')
    def test_nr_issues(self, query_total_mock):
        """ Test that the number of items equals the sum of totals per metric source returned by Jira. """
        query_total_mock.side_effect = [12, 13]

        result = JiraFilter('', '', '').nr_issues('123', '567')

        query_total_mock.assert_has_calls([call(123), call(567)])
        self.assertEqual(25, result)

    @patch.object(Jira, 'query_total')
    def test_nr_issues_on_error(self, query_total_mock):
        """ Test that the number of items is set to -1 if Jira returned -1 for any metric source. """
        query_total_mock.side_effect = [-1, 13]

        result = JiraFilter('', '', '').nr_issues('123', '567')

        query_total_mock.assert_has_calls([call(123), call(567)])
        self.assertEqual(-1, result)

    @patch.object(Jira, 'average_duration_of_issues')
    def test_average_duration_of_issues(self, average_duration_of_issues_mock):
        """ Test that the average duration is the average of the averages returned by different filters. """
        average_duration_of_issues_mock.side_effect = [12, 13]

        result = JiraFilter('', '', '').average_duration_of_issues('123', '567')

        average_duration_of_issues_mock.assert_has_calls([call(123), call(567)])
        self.assertEqual(12.5, result)

    @patch.object(Jira, 'extra_info')
    def test_extra_info_one(self, extra_info_mock):
        """ Test that the average duration is the average of the averages returned by different filters. """
        ret_obj = ExtraInfo()
        extra_info_mock.return_value = [ret_obj]

        result = JiraFilter('', '', '').extra_info()

        extra_info_mock.assert_called_once()
        self.assertEqual(ret_obj, result)

    @patch.object(Jira, 'extra_info')
    def test_extra_info_more(self, extra_info_mock):
        """ Test that the average duration is the average of the averages returned by different filters. """
        ret_obj1 = ExtraInfo(col1="x", clo2="y")
        ret_obj1 += 'a11', 'a12'
        ret_obj2 = ExtraInfo(col1="x", clo2="y")
        ret_obj2 += 'a21', 'a22'
        extra_info_mock.return_value = [ret_obj1, ret_obj2]

        expected = ExtraInfo(col1="x", clo2="y")
        expected += 'a11', 'a12'
        expected += 'a21', 'a22'

        result = JiraFilter('', '', '').extra_info()

        extra_info_mock.assert_called_once()
        self.assertEqual(expected.data, result.data)

    @patch.object(Jira, 'average_duration_of_issues')
    def test_average_duration_of_issues_on_error(self, average_duration_of_issues_mock):
        """ Test that the average is set to -1 if Jira returned -1 for any metric source. """
        average_duration_of_issues_mock.side_effect = [-1, 13]

        result = JiraFilter('', '', '').average_duration_of_issues('123', '567')

        average_duration_of_issues_mock.assert_has_calls([call(123), call(567)])
        self.assertEqual(-1, result)

    @patch.object(Jira, 'query_sum')
    def test_sum_field(self, query_sum_mock):
        """ Test that the number of points equals the sum of sums per metric source returned by Jira. """
        query_sum_mock.side_effect = [12.1, 13.2]

        result = JiraFilter('', '', '', field_name='customfield_1').sum_field('123', '567')

        query_sum_mock.assert_has_calls([call(123, 'customfield_1'), call(567, 'customfield_1')])
        self.assertAlmostEqual(25.3, result)

    @patch.object(Jira, 'query_sum')
    def test_sum_field_on_error(self, query_sum_mock):
        """ Test that the number of points is set to -1 if Jira returned -1 for any metric source. """
        query_sum_mock.side_effect = [-1, 13.2]

        result = JiraFilter('', '', '', field_name='customfield_1').sum_field('123', '567')

        query_sum_mock.assert_has_calls([call(123, 'customfield_1'), call(567, 'customfield_1')])
        self.assertEqual(-1, result)

    @patch.object(Jira, 'get_query_url')
    def test_url(self, get_query_url_mock):
        """ Test that the Jira filter returns the correct urls for the filters. """
        jira1 = 'http://jira1/view'
        jira2 = 'http://jira2/view'
        get_query_url_mock.side_effect = [jira1, jira2]

        result = JiraFilter('', '', '').metric_source_urls('123', '567')

        get_query_url_mock.assert_has_calls([call(123, search=False), call(567, search=False)])
        self.assertEqual([jira1, jira2], result)

    @patch.object(Jira, 'query_field_empty')
    def test_nr_issues_field_empty(self, query_field_empty_mock):
        """ Test that the number of points equals the sum of sums per metric source returned by Jira. """
        query_field_empty_mock.side_effect = [1, 2]

        result = JiraFilter('', '', '', field_name='customfield_1').nr_issues_with_field_empty(
            '123', '567')

        query_field_empty_mock.assert_has_calls([call(123, 'customfield_1'), call(567, 'customfield_1')])
        self.assertEqual(3, result)

    @patch.object(Jira, 'query_field_empty')
    def test_nr_issues_field_empty_on_error(self, query_field_empty_mock):
        """ Test that the number of points is set to -1 if Jira returned -1 for any metric source. """
        query_field_empty_mock.side_effect = [-1, 2]

        result = JiraFilter('', '', '', field_name='customfield_1').nr_issues_with_field_empty(
            '123', '567')

        query_field_empty_mock.assert_has_calls([call(123, 'customfield_1'), call(567, 'customfield_1')])
        self.assertEqual(-1, result)
