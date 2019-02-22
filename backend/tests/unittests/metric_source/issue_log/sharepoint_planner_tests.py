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

import json
import datetime
import logging
import urllib.error
from urllib import parse
import unittest
from unittest.mock import patch, call, MagicMock
from dateutil.tz import tzutc, tzlocal
from dateutil.relativedelta import relativedelta
from hqlib.metric_source import url_opener
from hqlib.persistence import FilePersister
from hqlib.metric_source.issue_log.sharepoint_planner import SharepointPlanner


@patch.object(FilePersister, 'read_json')
@patch.object(FilePersister, 'write_json')
class SharepointPlannerTest(unittest.TestCase):
    """ Unit tests for the SharepointPlanner class. """

    # pylint: disable=too-many-public-methods
    # pylint: disable=too-many-instance-attributes

    def setUp(self):

        # pylint: disable=protected-access

        SharepointPlanner._retrieve_tasks.cache_clear()
        SharepointPlanner._get_tasks_for_criterion.cache_clear()

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_ignored_lists(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test that list of ignored buckets is returned as defined. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            '{"value": [{"completedDateTime": null, "createdDateTime":"2018-02-28T13:01:08.8386828Z",'
            '"assignments": {"ecf0xx": {"assignedDateTime": "2018-02-28T13:01:08.8386828Z"}}}]}']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json',
                                    lists_to_ignore=['bucket1'])

        result = planner.ignored_lists()

        self.assertEqual(['bucket1'], result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_datetime(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test the last activity date. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            '{"value": [{"completedDateTime": null, "createdDateTime":"2018-02-28T13:01:08.8386828Z",'
            '"assignments": {"ecf0xx": {"assignedDateTime": "2018-02-28T13:01:08.8386828Z"}}}]}']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        last_activity_date = planner.datetime('plan_id_xx')

        mock_write_json.assert_called_once_with(
            {'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(
            last_activity_date,
            datetime.datetime(2018, 2, 28, 13, 1, 8, tzinfo=tzutc()).astimezone(tzlocal()).replace(tzinfo=None))
        self.assertEqual(mock_url_read.call_args_list[0],
                         call(url='https://login.microsoftonline.com/common/oauth2/token',
                              post_body=bytes(parse.urlencode({
                                  "grant_type": "refresh_token",
                                  "client_id": 'client_id_xx',
                                  "client_secret": 'client_secret_k=',
                                  "resource": "https://graph.microsoft.com",
                                  "refresh_token": 'refresh_token_content_xx'
                              }), 'ascii')))
        self.assertEqual(mock_url_read.call_args_list[1],
                         call(url='https://graph.microsoft.com/v1.0/planner/plans/plan_id_xx/tasks'))

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_datetime_multiple_plans(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test the last activity date is the last from all listed plans. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            '{"value": [{"completedDateTime": null, "createdDateTime":"2018-02-28T11:01:08.8386828Z",'
            '"assignments": {"ecf0xx": {"assignedDateTime": "2018-02-28T13:01:08.8386828Z"}}}]}',
            '{"value": [{"completedDateTime": null, "createdDateTime":"2018-03-28T11:01:08.88Z", "assignments": {}}]}']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        last_activity_date = planner.datetime('plan_id_1', 'plan_id_2')

        mock_write_json.assert_called_once_with(
            {'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(
            last_activity_date,
            datetime.datetime(2018, 3, 28, 11, 1, 8, tzinfo=tzutc()).astimezone(tzlocal()).replace(tzinfo=None))
        self.assertEqual(mock_url_read.call_args_list[1],
                         call(url='https://graph.microsoft.com/v1.0/planner/plans/plan_id_1/tasks'))
        self.assertEqual(mock_url_read.call_args_list[2],
                         call(url='https://graph.microsoft.com/v1.0/planner/plans/plan_id_2/tasks'))

    @patch.object(logging, 'error')
    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_datetime_http_error(self, mock_url_read, mock_error, mock_write_json, mock_read_json):
        """ Test that the last activity date is min date, when an http error occurs. """
        file_object = MagicMock()
        file_object.read = MagicMock(return_value=b'additional reason')
        mock_url_read.side_effect = [urllib.error.HTTPError(None, None, None, None, file_object)]
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        last_activity_date = planner.datetime('plan_id_xx')

        mock_write_json.assert_not_called()
        mock_url_read.assert_called_once_with(
            url='https://login.microsoftonline.com/common/oauth2/token',
            post_body=bytes(parse.urlencode({
                "grant_type": "refresh_token",
                "client_id": 'client_id_xx',
                "client_secret": 'client_secret_k=',
                "resource": "https://graph.microsoft.com",
                "refresh_token": 'refresh_token_content_xx'
            }), 'ascii')
        )
        self.assertEqual(last_activity_date, datetime.datetime.min)
        self.assertEqual(
            'Error retrieving access token. Reason: %s. Additional information: %s', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], urllib.error.HTTPError)
        self.assertEqual('additional reason', mock_error.call_args_list[0][0][2])

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_datetime_http_error_tasks(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test that the last activity date is min date, when an http error occurs during tasks retrieval. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            urllib.error.HTTPError(None, None, None, None, None)]
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        last_activity_date = planner.datetime('plan_id_xx')

        mock_write_json.assert_called_once()
        self.assertEqual(last_activity_date, datetime.datetime.min)

    @patch.object(logging, 'error')
    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_datetime_json_error_tasks(self, mock_url_read, mock_error, mock_write_json, mock_read_json):
        """ Test that the last activity date is min date, when invalid json retrieved during tasks retrieval. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            'non-json']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        last_activity_date = planner.datetime('plan_id_xx')

        mock_write_json.assert_called_once()
        self.assertEqual(last_activity_date, datetime.datetime.min)
        self.assertEqual('Invalid json retrieved for tasks. Reason: %s.', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], ValueError)

    @patch.object(logging, 'error')
    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_datetime_json_key_error_tasks(self, mock_url_read, mock_error, mock_write_json, mock_read_json):
        """ Test that the last activity date is min date, when invalid json retrieved during tasks retrieval. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            '{}']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        last_activity_date = planner.datetime('plan_id_xx')

        mock_write_json.assert_called_once()
        self.assertEqual(last_activity_date, datetime.datetime.min)
        self.assertEqual('Invalid json retrieved for tasks. Reason: %s.', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], KeyError)

    @patch.object(logging, 'error')
    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_init_json_error(self, mock_url_read, mock_error, mock_write_json, mock_read_json):
        """ Test that the last activity date is min date, when invalid json retrieved. """
        mock_url_read.return_value = 'non-json'
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        last_activity_date = planner.datetime('plan_id_xx')

        mock_write_json.assert_not_called()
        self.assertEqual(last_activity_date, datetime.datetime.min)
        self.assertEqual('Invalid json retrieved for access token. Reason: %s.', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], json.decoder.JSONDecodeError)

    @patch.object(logging, 'error')
    @patch.object(logging, 'info')
    def test_init_refresh_token_key_error(self, mock_info, mock_error, mock_write_json, mock_read_json):
        """ Test that the last activity date is min date, when invalid json retrieved. """
        mock_read_json.return_value = {}

        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        self.assertIsNotNone(planner)
        mock_write_json.assert_not_called()
        mock_info.assert_called_once_with(
            'No refresh token could be loaded. Please, generate one using the script refresh_token_generator.py.')
        self.assertEqual('Error reading refresh token. Reason: %s.', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], KeyError)

    @patch.object(logging, 'error')
    @patch.object(logging, 'info')
    def test_init_refresh_token_type_error(self, mock_info, mock_error, mock_write_json, mock_read_json):
        """ Test that the last activity date is min date, when invalid json retrieved. """
        mock_read_json.return_value = None

        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        self.assertIsNotNone(planner)
        mock_write_json.assert_not_called()
        mock_info.assert_called_once_with(
            'No refresh token could be loaded. Please, generate one using the script refresh_token_generator.py.')
        self.assertEqual('Error reading refresh token. Reason: %s.', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], TypeError)

    def test_metric_source_urls(self, mock_write_json, mock_read_json):
        """ Test that the last activity date is min date, when invalid json retrieved. """
        mock_read_json.return_value = {'refresh_token': ''}
        self.assertEqual(
            SharepointPlanner(url='https://planner_home', client_id='', client_secret='', refresh_token_location='')
            .metric_source_urls('plan_id'), ['https://planner_home/Home/Planner'])
        mock_write_json.assert_not_called()

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_over_due_actions(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test that the number of overdue tasks matches. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            '{"value": [{"completedDateTime": null, "createdDateTime":"2018-02-28T13:01:08.8386828Z",'
            '"dueDateTime": "2018-07-28T10:00:00.2Z",'
            '"assignments": {"ecf0xx": {"assignedDateTime": "2018-02-28T13:01:08.8386828Z"}}}]}']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_called_once_with({'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(planner.nr_of_over_due_actions('plan_id_xx'), 1)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_over_due_actions_completed(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test that the tasks are not counted if they are completed. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            '{"value": [{"completedDateTime": "2018-09-28T10:00:00.2Z", "createdDateTime":"2018-02-28T13:01:08.8328Z",'
            '"assignments": {"ecf0xx": {"assignedDateTime": "2018-02-28T13:01:08.8386828Z"}}}]}']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_called_once_with({'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(planner.nr_of_over_due_actions('plan_id_xx'), 0)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_over_due_actions_no_date(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test that the number of overdue tasks does not count tasks with missing due date tag. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            '{"value": [{"completedDateTime": null, "createdDateTime":"2018-02-28T13:01:08.8386828Z",'
            '"assignments": {"ecf0xx": {"assignedDateTime": "2018-02-28T13:01:08.8386828Z"}}}]}']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_called_once_with({'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(planner.nr_of_over_due_actions('plan_id_xx'), 0)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_over_due_actions_http_error(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test that the number of overdue tasks returns -1 when http error occurs. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            urllib.error.HTTPError(None, None, None, None, None)]
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_called_once_with({'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(planner.nr_of_over_due_actions('plan_id_xx'), -1)

    @patch.object(logging, 'error')
    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_over_due_actions_invalid_json(self, mock_url_read, mock_error, mock_write_json, mock_read_json):
        """ Test that the number of overdue tasks returns -1 when tasks json is invalid. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            'non-json']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_called_once_with({'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(planner.nr_of_over_due_actions('plan_id_xx'), -1)
        self.assertEqual('Invalid json retrieved for tasks. Reason: %s.', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], ValueError)

    @patch.object(logging, 'info')
    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_over_due_actions_empty_refresh_json(self, mock_url_read, mock_info, mock_write_json, mock_read_json):
        """ Test that the number of overdue tasks returns -1 when refresh token file is empty. """
        mock_read_json.return_value = ''
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_not_called()
        mock_info.assert_called_once_with(
            'No refresh token could be loaded. Please, generate one using the script refresh_token_generator.py.')
        self.assertEqual(planner.nr_of_over_due_actions('plan_id_xx'), -1)
        mock_url_read.assert_not_called()

    @patch.object(logging, 'error')
    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_over_due_actions_invalid_time(self, mock_url_read, mock_error, mock_write_json, mock_read_json):
        """ Test that the number of overdue tasks returns -1 when json is invalid. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            '{"non-value": [{"completedDateTime": null, '
            '"createdDateTime":"2018-02-28T11:01:08.8386828Z","assignments": {}}]}']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_called_once_with({'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(planner.nr_of_over_due_actions('plan_id_xx'), -1)
        self.assertEqual('Invalid json retrieved for tasks. Reason: %s.', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], KeyError)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_over_due_actions_date_null(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test that the number of overdue tasks does not count tasks with empty due date. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            '{"value": [{"completedDateTime": null, "createdDateTime":"2018-02-28T13:01:08.838Z", "dueDateTime": null,'
            '"assignments": {"ecf0xx": {"assignedDateTime": "2018-02-28T13:01:08.8386828Z"}}}]}']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_called_once_with({'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(planner.nr_of_over_due_actions('plan_id_xx'), 0)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_over_due_actions_future(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test that the number of overdue tasks does not count tasks with due date in the future. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            '{"value": [{"completedDateTime": null, "createdDateTime":"2018-02-28T13:01:08.828Z", "dueDateTime": "' + (
                datetime.datetime.utcnow() + relativedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ") + '",'
            '"assignments": {"ecf0xx": {"assignedDateTime": "2018-02-28T13:01:08.8386828Z"}}}]}']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_called_once_with({'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(planner.nr_of_over_due_actions('plan_id_xx'), 0)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_over_due_actions_url(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test that the urls of overdue tasks match. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            '{"value": [{"completedDateTime": null, "createdDateTime":"2018-02-28T13:01:08.828Z", "id": "id_VbPAGNM", '
            '"title": "Title!", "dueDateTime": "' + (datetime.datetime.utcnow() - relativedelta(days=7)
                                                     ).strftime("%Y-%m-%dT%H:%M:%S.%fZ") + '",'
            '"assignments": {"ecf0xx": {"assignedDateTime": "2018-02-28T13:01:08.8386828Z"}}}]}']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='https://planner_home/', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_called_once_with({'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(planner.over_due_actions_url('plan_id_xx'),
                         [('https://planner_home/Home/Task/id_VbPAGNM', 'Title!', '7 dagen')])

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_over_due_actions_url_http_error(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test that the urls of overdue tasks match. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            urllib.error.HTTPError(None, None, None, None, None)]
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='https://planner_home/', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_called_once_with({'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(planner.over_due_actions_url('plan_id_xx'), [])

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_inactive_actions(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test that the number of inactive tasks matches. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            '{"value": [{"completedDateTime": null, "createdDateTime":"2018-02-28T13:01:08.8386828Z",'
            '"assignments": {"ecf0xx": {"assignedDateTime": "2018-02-28T13:01:08.8386828Z"}}}]}']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_called_once_with({'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(planner.nr_of_inactive_actions('plan_id_xx'), 1)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_inactive_actions_due_null(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test that the task without due date is counted as inactive. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            '{"value": [{"completedDateTime": null, "createdDateTime":"2018-02-28T13:01:08.828Z", "dueDateTime": null,'
            '"assignments": {"ecf0xx": {"assignedDateTime": "2018-02-28T13:01:08.8386828Z"}}}]}']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_called_once_with({'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(planner.nr_of_inactive_actions('plan_id_xx'), 1)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_inactive_actions_due_future(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test that the inactive task with the due date in the future is counted. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            '{"value": [{"completedDateTime": null, "createdDateTime":"2018-02-28T13:01:08.838Z", "dueDateTime": "' + (
                datetime.datetime.utcnow() + relativedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ") + '",'
            '"assignments": {"ecf0xx": {"assignedDateTime": "2018-02-28T13:01:08.8386828Z"}}}]}']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_called_once_with({'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(planner.nr_of_inactive_actions('plan_id_xx'), 1)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_inactive_actions_overdue(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test that the an overdue action is not considered to be inactive. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            '{"value": [{"completedDateTime": null, "createdDateTime":"2018-02-28T13:01:08.8386828Z",'
            '"dueDateTime": "2018-07-28T10:00:00.2Z",'
            '"assignments": {"ecf0xx": {"assignedDateTime": "2018-02-28T13:01:08.8386828Z"}}}]}']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_called_once_with({'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(planner.nr_of_inactive_actions('plan_id_xx'), 0)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_inactive_actions_less_than_limit(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test that the task inactive for less than 14 days is not counted as inactive. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            '{"value": [{"completedDateTime": null, "createdDateTime":"' + (
                datetime.datetime.utcnow() - relativedelta(days=13)).strftime("%Y-%m-%dT%H:%M:%S.%fZ") + '",'
            '"assignments": {"ecf0xx": {"assignedDateTime": "2018-02-28T13:01:08.8386828Z"}}}]}']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_called_once_with({'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(planner.nr_of_inactive_actions('plan_id_xx'), 0)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_inactive_actions_http_error(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test that the number of inactive tasks returns -1 when http error occurs. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            urllib.error.HTTPError(None, None, None, None, None)]
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_called_once_with({'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(planner.nr_of_inactive_actions('plan_id_xx'), -1)

    @patch.object(logging, 'error')
    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_inactive_actions_invalid_json(self, mock_url_read, mock_error, mock_write_json, mock_read_json):
        """ Test that the number of inactive tasks returns -1 when json is invalid. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            'non-json']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_called_once_with({'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(planner.nr_of_inactive_actions('plan_id_xx'), -1)
        self.assertEqual('Invalid json retrieved for tasks. Reason: %s.', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], json.decoder.JSONDecodeError)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_inactive_actions_no_tasks(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test that the number of inactive tasks is 0 when no tasks are provided. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}', '{"value": []}']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_called_once_with({'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(planner.nr_of_inactive_actions('plan_id_xx'), 0)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_inactive_actions_no_sources(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test that the number of inactive tasks is 0 when no metric source ids are provided. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}']
        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='/home', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_called_once_with({'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(planner.nr_of_inactive_actions(), 0)
        mock_url_read.assert_called_once()

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_inactive_actions_url(self, mock_url_read, mock_write_json, mock_read_json):
        """ Test that the task urls of inactive actions are retrieved correctly. """
        mock_url_read.side_effect = [
            '{"access_token": "ey_xx", "refresh_token": "new_refresh_token"}',
            '{"value": [{"completedDateTime": null, "createdDateTime":"2018-02-28T13:01:08.8386828Z", '
            '"id": "id_VbPAGNM", "title": "Title!", "dueDateTime": null,'
            '"assignments": {"ecf0xx": {"assignedDateTime": "' + (
                datetime.datetime.utcnow() - relativedelta(days=19)).strftime("%Y-%m-%dT%H:%M:%S.%fZ") + '"}}}]}']

        mock_read_json.return_value = {'refresh_token': 'refresh_token_content_xx'}
        planner = SharepointPlanner(url='https://planner_home/', client_id='client_id_xx',
                                    client_secret='client_secret_k=',
                                    refresh_token_location='file_location_of_token.json')

        mock_write_json.assert_called_once_with({'refresh_token': 'new_refresh_token'}, 'file_location_of_token.json')
        self.assertEqual(planner.inactive_actions_url('plan_id_xx'),
                         [('https://planner_home/Home/Task/id_VbPAGNM', 'Title!', '19 dagen')])
