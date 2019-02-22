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
import datetime
import unittest
from unittest.mock import patch
from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc, tzlocal
from hqlib.metric_source import Jira, JiraFilter
from hqlib.metric_source.issue_log.jira_action_list import JiraActionList


class JiraActionListTest(unittest.TestCase):
    """ Unit tests for the JiraActionList class. """

    @patch.object(JiraFilter, 'issues_with_field_exceeding_value')
    @patch.object(JiraFilter, '__init__')
    def test_over_due_actions_url_init(self, mock_init, mock_issues):
        """ Test that the JiraFilter object is correctly created."""

        mock_init.return_value = None
        action_filter = JiraActionList('http://jira/', 'username', 'password', field_name='custom_due_date')

        action_filter.over_due_actions_url('jira_filter_id')

        self.assertEqual(('jira_filter_id',), mock_issues.call_args[0])
        # pylint: disable=protected-access
        self.assertEqual(action_filter._is_str_date_before, mock_issues.call_args[1]['compare'])
        self.assertAlmostEqual(datetime.datetime.now(), mock_issues.call_args[1]['limit_value'],
                               places=None, msg=None, delta=datetime.timedelta(seconds=1))
        mock_init.assert_called_with('http://jira/', 'username', 'password', 'custom_due_date')

    def test_ignored_lists(self):
        """  """
        ignore_fields = [{"field1": 'x1'}, {"field2": 'y2'}]
        action_filter = JiraActionList('http://jira/', 'username', 'password', fields_to_ignore=ignore_fields)
        self.assertEqual(ignore_fields, action_filter.ignored_lists())

    @patch.object(Jira, 'get_query')
    def test_over_due_actions_url_ignore(self, get_query_url_mock):
        """ Test that the issues are ignored if certain field has given value. """
        ignore_fields = [{"ignore": "THIS"}]
        action_filter = JiraActionList('http://jira/', 'username', 'password',
                                       field_name='ddt', fields_to_ignore=ignore_fields)
        dt2 = (datetime.datetime.now().astimezone() - relativedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S%z")
        get_query_url_mock.return_value = \
            {"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5", "issues": [
                {"key": "ISS-1", "fields": {"ignore": "THIS", "summary": "First Issue", "ddt": dt2}}]}

        result = action_filter.over_due_actions_url('jira_filter_id')

        get_query_url_mock.assert_called_once()

        self.assertEqual([], result)

    @patch.object(Jira, 'get_query')
    def test_over_due_actions_url_ignore2(self, get_query_url_mock):
        """ Test that the issues are not ignored if the value is one or the other. """
        ignore_fields = [{"ignore": "THIS"}, {"ignore": "that"}]
        action_filter = JiraActionList('http://jira/', 'username', 'password',
                                       field_name='ddt', fields_to_ignore=ignore_fields)
        dt2 = (datetime.datetime.now().astimezone() - relativedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S%z")
        get_query_url_mock.return_value = \
            {"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5", "issues": [
                {"key": "ISS-1", "fields": {"ignore": "that", "summary": "First Issue", "ddt": dt2}},
                {"key": "ISS-X", "fields": {"ignore": "THIS", "summary": "X Issue", "ddt": dt2}}]}

        result = action_filter.over_due_actions_url('jira_filter_id')

        get_query_url_mock.assert_called_once()

        self.assertEqual([], result)

    @patch.object(Jira, 'get_query')
    def test_inactive_actions_url(self, get_query_url_mock):
        """ Test that an overdue action, inactive for 14 days or more is returned as inactive."""
        dt2 = (datetime.datetime.now().astimezone() - relativedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S%z")
        dt3 = (datetime.datetime.now().astimezone() - relativedelta(days=14, minutes=5)).strftime("%Y-%m-%dT%H:%M:%S%z")
        get_query_url_mock.return_value = \
            {"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5", "issues": [
                {"key": "ISS-2", "fields": {"ignore": "that", "summary": "2nd Issue", "ddt": dt2, "updated": dt3}}]}

        action_filter = JiraActionList('http://jira/', 'username', 'password', field_name='ddt')

        result = action_filter.inactive_actions_url('jira_filter_id')

        self.assertEqual([("http://jira/browse/ISS-2", "2nd Issue", "14 dagen")], result)

    @patch.object(Jira, 'get_query')
    def test_over_due_actions_url_jira(self, get_query_url_mock):
        """ Test that the issues are returned correctly with their field values. """
        action_filter = JiraActionList('http://jira/', 'username', 'password', field_name='ddt')
        dt2 = (datetime.datetime.now().astimezone() - relativedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S%z")
        get_query_url_mock.return_value = \
            {"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5", "issues": [
                {"key": "ISS-1", "fields": {"summary": "First Issue", "ddt": dt2}}]}

        result = action_filter.over_due_actions_url('jira_filter_id')

        get_query_url_mock.assert_called_once()

        self.assertEqual([("http://jira/browse/ISS-1", "First Issue", "2 dagen")], result)

    @patch.object(JiraFilter, 'issues_with_field_exceeding_value')
    def test_over_due_actions_url(self, mock_issues):
        """ Test that the overdue actions are correctly returned."""
        dt2 = (datetime.datetime.now().astimezone() - relativedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S%z")
        mock_issues.return_value = [("http://jira/browse/ISS-2", "2nd Issue", dt2, "<updated_date>", '<created_date>')]
        action_filter = JiraActionList('http://jira/', 'username', 'password', field_name='custom_due_date')

        result = action_filter.over_due_actions_url('jira_filter_id')

        self.assertEqual([("http://jira/browse/ISS-2", "2nd Issue", "2 dagen")], result)

    @patch.object(JiraFilter, 'issues_with_field_exceeding_value')
    def test_nr_of_over_due_actions(self, mock_issues):
        """ Test that the number of overdue actions is correct."""
        mock_issues.return_value = [
            ("http://jira/browse/ISS-2", "2nd Issue", "<custom_due_date>", "<updated_date>", '<created_date>')]
        action_filter = JiraActionList('http://jira/', 'username', 'password', field_name='custom_due_date')

        result = action_filter.nr_of_over_due_actions('jira_filter_id')

        self.assertEqual(1, result)

    @patch.object(logging, 'error')
    @patch.object(JiraFilter, 'issues_with_field_exceeding_value')
    def test_inactive_actions_url_index_error(self, mock_issues, mock_error):
        """ Test that it returns empty list if the tuple returned by jira filter is too short."""
        mock_issues.return_value = [("http://jira/browse/ISS-2", "2nd Issue", "<custom_due_date>")]
        action_filter = JiraActionList('http://jira/', 'username', 'password', field_name='custom_due_date')

        result = action_filter.inactive_actions_url('jira_filter_id')

        self.assertEqual([], result)
        self.assertEqual("Jira filter result for inactive issues inadequate. Reason: %s.",
                         mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], IndexError)

    @patch.object(logging, 'error')
    @patch.object(JiraFilter, 'issues_with_field_exceeding_value')
    def test_nr_of_over_due_actions_index_error(self, mock_issues, mock_error):
        """ Test that it returns empty list if the tuple returned by jira filter is too short."""
        mock_issues.return_value = [("http://jira/browse/ISS-2", "2nd Issue", "<custom_due_date>")]
        action_filter = JiraActionList('http://jira/', 'username', 'password',
                                       field_name='custom_due_date', fields_to_ignore=[{'extra': 'x'}])

        result = action_filter.nr_of_over_due_actions('jira_filter_id')

        self.assertEqual(-1, result)
        self.assertEqual("Jira filter result for overdue issues inadequate. Reason: %s.",
                         mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], IndexError)

    @patch.object(JiraFilter, 'issues_with_field_exceeding_value')
    def test_inactive_actions_url_ok(self, mock_issues):
        """ Test that an overdue action, inactive for 14 days or more is returned as inactive."""
        dt2 = (datetime.datetime.now().astimezone() - relativedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S%z")
        dt3 = (datetime.datetime.now().astimezone() - relativedelta(days=14, minutes=5)).strftime("%Y-%m-%dT%H:%M:%S%z")
        mock_issues.return_value = [("http://jira/browse/ISS-2", "2nd Issue", dt2, dt3, '<created_date>')]
        action_filter = JiraActionList('http://jira/', 'username', 'password', field_name='custom_due_date')

        result = action_filter.inactive_actions_url('jira_filter_id')

        self.assertEqual([("http://jira/browse/ISS-2", "2nd Issue", "14 dagen")], result)

    @patch.object(JiraFilter, 'issues_with_field_exceeding_value')
    def test_inactive_actions_url_new(self, mock_issues):
        """ Test that the overdue action, inactive for less than 14 days is not returned as inactive."""
        dt2 = (datetime.datetime.now().astimezone() - relativedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S.000%z")
        dt3 = (datetime.datetime.now().astimezone() - relativedelta(days=13)).strftime("%Y-%m-%dT%H:%M:%S%z")
        mock_issues.return_value = [("http://jira/browse/ISS-2", "2nd Issue", dt2, dt3, '<created_date>')]
        action_filter = JiraActionList('http://jira/', 'username', 'password', field_name='custom_due_date')

        result = action_filter.inactive_actions_url('jira_filter_id')

        self.assertEqual([], result)

    @patch.object(JiraFilter, 'issues_with_field_exceeding_value')
    def test_nr_of_inactive_actions(self, mock_issues):
        """ Test that the overdue action, inactive for 14 days or more is returned as inactive."""
        dt2 = (datetime.datetime.now().astimezone() - relativedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S%z")
        dt3 = (datetime.datetime.now().astimezone() - relativedelta(days=14, minutes=5)).strftime("%Y-%m-%dT%H:%M:%S%z")
        mock_issues.return_value = [("http://jira/browse/ISS-2", "2nd Issue", dt2, dt3, '<created_date>')]
        action_filter = JiraActionList('http://jira/', 'username', 'password', field_name='custom_due_date')

        result = action_filter.nr_of_inactive_actions('jira_filter_id')

        self.assertEqual(1, result)

    @patch.object(logging, 'error')
    @patch.object(JiraFilter, 'issues_with_field_exceeding_value')
    def test_nr_of_inactive_actions_index_error(self, mock_issues, mock_error):
        """ Test that the number of inactive actions is -1 if error occurs and the event is logged."""
        mock_issues.return_value = [("http://jira/browse/ISS-2", "2nd Issue", "2018-10-22T19:12:36.000+0100")]
        action_filter = JiraActionList('http://jira/', 'username', 'password', field_name='custom_due_date')

        result = action_filter.nr_of_inactive_actions('jira_filter_id')

        self.assertEqual(-1, result)
        self.assertEqual("Jira filter result for inactive issues inadequate. Reason: %s.",
                         mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], IndexError)

    @patch.object(JiraFilter, 'issues_with_field_exceeding_value')
    def test_datetime(self, mock_issues):
        """ Test that the last action date is the create date, if there is no update date.."""
        mock_issues.return_value = [
            ("http://jira/browse/ISS-2", "2nd Issue", "<custom_due_date>", None, "2018-10-22T19:12:36.000Z")]
        action_filter = JiraActionList('http://jira/', 'username', 'password', field_name='custom_due_date')

        result = action_filter.datetime('jira_filter_id')

        self.assertEqual(datetime.datetime(2018, 10, 22, 19, 12, 36,
                                           tzinfo=tzutc()).astimezone(tzlocal()).replace(tzinfo=None), result)

    @patch.object(JiraFilter, 'issues_with_field_exceeding_value')
    def test_datetime_update_date(self, mock_issues):
        """ Test that last action date is the newest update date."""
        mock_issues.return_value = [
            ("http://jira/browse/ISS-2", "2nd Issue", "<custom_due_date>",
             "2018-10-11T11:11:36.000+0100", "2018-10-22T19:12:36.000Z"),
            ("http://jira/browse/ISS-2", "2nd Issue", "<custom_due_date>",
             "2018-10-23T19:19:36.000+0100", "2018-10-12T19:33:36.000+0100")]
        action_filter = JiraActionList('http://jira/', 'username', 'password', field_name='custom_due_date')

        result = action_filter.datetime('jira_filter_id')

        self.assertEqual(datetime.datetime(2018, 10, 23, 19 - 1, 19, 36,
                                           tzinfo=tzutc()).astimezone(tzlocal()).replace(tzinfo=None), result)
