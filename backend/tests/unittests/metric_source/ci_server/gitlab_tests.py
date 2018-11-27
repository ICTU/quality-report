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

import logging
import datetime
import unittest
from unittest.mock import patch
from dateutil.relativedelta import relativedelta

import gitlab
from gitlab import Gitlab

from hqlib.metric_source import GitLabCI


class GitLabCITest(unittest.TestCase):
    """ Unit tests for the GitLab class. """

    def setUp(self):
        # pylint: disable=protected-access
        GitLabCI._get_last_successful_pipeline_date.cache_clear()
        GitLabCI._get_jobs_list.cache_clear()

    def test_failing_jobs_no_project_is_configured(self):
        """ Test that there are no failing jobs when projects are not defined. """
        self.assertEqual([], GitLabCI('https://gitlab.url.com/').failing_jobs_url())

    @patch.object(logging, 'error')
    @patch.object(Gitlab, 'http_get')
    def test_failing_jobs_url_bad_josn_project(self, mock_http_get, mock_error):
        """ Test that there are no failing urls if invalid project object is returned. """
        mock_http_get.side_effect = ['no-json!']
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.failing_jobs_url()

        self.assertEqual([], result)
        self.assertEqual('Error retrieving project data. Reason: %s.', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], TypeError)

    @patch.object(logging, 'error')
    @patch.object(Gitlab, 'http_get')
    def test_failing_jobs_url_gitlab_error(self, mock_http_get, mock_error):
        """Test that there are no failing urls if a gitlab error occurred.  """
        mock_http_get.side_effect = [gitlab.GitlabHttpError]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.failing_jobs_url()

        self.assertEqual([], result)
        self.assertEqual('Error retrieving project data. Reason: %s.', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], gitlab.GitlabError)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_failing_jobs_url_one(self, mock_http_list, mock_http_get):
        """ Test the urls of failing jobs when there is one. """
        mock_http_list.side_effect = [
            [{'id': 123, 'status': 'success', 'web_url': 'https://gitlab.com/pipelines/39'}],
            [{'id': 131, 'status': 'failed', 'name': 'job_1', 'web_url': 'https://gitlab.com/jobs-url/'}]]
        mock_http_get.side_effect = [
            {'id': 55, 'name_with_namespace': 'project_name'},
            {'id': 111, 'finished_at': (datetime.datetime.utcnow() - relativedelta(days=7))
                .strftime("%Y-%m-%dT%H:%M:%S.%fZ")}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.failing_jobs_url()

        self.assertEqual([[('project_name / job_1', 'https://gitlab.com/jobs-url/', '7')]], result)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_number_of_active_jobs(self, mock_http_list, mock_http_get):
        """ Test that the number of active jobs is correct. """
        mock_http_list.return_value = [
            {'id': 131, 'status': 'unimportant!', 'name': 'job_1', 'web_url': 'https://gitlab.com/jobs-url/'}]
        mock_http_get.return_value = {'id': 55, 'name_with_namespace': 'project_name'}
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name', job_re=r'\S*_\d')

        result = gitlab_ci.number_of_active_jobs()

        self.assertEqual(1, result)

    @patch.object(logging, 'error')
    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_number_of_active_jobs_attribute_error(self, mock_http_list, mock_http_get, mock_error):
        """ Test that the number of active jobs is 0 if error occurred and that it is logged. """
        mock_http_list.side_effect = [AttributeError]
        mock_http_get.return_value = {'id': 55, 'name_with_namespace': 'project_name'}
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name', job_re=r'\S*_\d')

        result = gitlab_ci.number_of_active_jobs()

        self.assertEqual(0, result)
        self.assertEqual('Error retrieving jobs data. Reason: %s.', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], AttributeError)

    @patch.object(logging, 'error')
    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_number_of_active_jobs_gitlab_error(self, mock_http_list, mock_http_get, mock_error):
        """ Test that the number of active jobs is 0 if error occurred and that it is logged. """
        mock_http_list.side_effect = [gitlab.GitlabError]
        mock_http_get.return_value = {'id': 55, 'name_with_namespace': 'project_name'}
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name', job_re=r'\S*_\d')

        result = gitlab_ci.number_of_active_jobs()

        self.assertEqual(0, result)
        self.assertEqual('Error retrieving jobs data. Reason: %s.', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], gitlab.GitlabError)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_number_of_active_jobs_no_project(self, mock_http_list, mock_http_get):
        """ Test that the number of active jobs is correct. """
        gitlab_ci = GitLabCI('https://gitlab.url.com/', *'', job_re=r'\S*_\d')

        result = gitlab_ci.number_of_active_jobs()

        mock_http_list.assert_not_called()
        mock_http_get.assert_not_called()
        self.assertEqual(0, result)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_failing_jobs_url_filtered_out(self, mock_http_list, mock_http_get):
        """ Test the urls of failing jobs not matching the given regular expression are not considered. """
        mock_http_list.side_effect = [
            [{'id': 123, 'status': 'success', 'web_url': 'https://gitlab.com/pipelines/39'}],
            [{'id': 131, 'status': 'failed', 'name': 'job_1', 'web_url': 'https://gitlab.com/jobs-url/'}]]
        mock_http_get.side_effect = [
            {'id': 55, 'name_with_namespace': 'project_name'},
            {'id': 111, 'finished_at': "2018-02-28T13:01:08.8386828Z"}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name', job_re=r'\S*-\d')

        result = gitlab_ci.failing_jobs_url()

        self.assertEqual([], result)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_number_of_failing_jobs(self, mock_http_list, mock_http_get):
        """ Test the number of failing jobs when there is one. """
        mock_http_list.side_effect = [
            [{'id': 123, 'status': 'success', 'web_url': 'https://gitlab.com/pipelines/39'}],
            [{'id': 131, 'status': 'failed', 'name': 'job_1', 'web_url': 'https://gitlab.com/jobs-url/'}]]
        mock_http_get.side_effect = [
            {'id': 55, 'name_with_namespace': 'project_name'},
            {'id': 111, 'finished_at': (datetime.datetime.utcnow() - relativedelta(days=7))
                .strftime("%Y-%m-%dT%H:%M:%S.%fZ")}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.number_of_failing_jobs()

        self.assertEqual(1, result)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_failing_jobs_url_one_day_old(self, mock_http_list, mock_http_get):
        """ Test that the failing urls of projects that built successfully a day or less ago are not counted. """
        mock_http_list.side_effect = [
            [{'id': 123, 'status': 'success', 'web_url': 'https://gitlab.com/pipelines/39'}],
            [{'id': 131, 'status': 'failed', 'name': 'job_1', 'web_url': 'https://gitlab.com/jobs-url/'}]]
        mock_http_get.side_effect = [
            {'id': 55, 'name_with_namespace': 'project_name'},
            {'id': 111, 'finished_at': (datetime.datetime.utcnow() - relativedelta(days=1))
                .strftime("%Y-%m-%dT%H:%M:%S.%fZ")}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.failing_jobs_url()

        self.assertEqual([], result)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_failing_jobs_url_no_pipelines(self, mock_http_list, mock_http_get):
        """ Test the failing jobs urls are empty if there is no pipelines. """
        mock_http_list.side_effect = [[]]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.failing_jobs_url()

        self.assertEqual([], result)
        mock_http_get.assert_called_once_with('/projects/project_name')

    @patch.object(logging, 'error')
    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_failing_jobs_url_error_pipelines_data(self, mock_http_list, mock_http_get, mock_error):
        """ Test the failing jobs urls are empty if there is no pipeline data. """
        mock_http_list.side_effect = [gitlab.GitlabHttpError]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.failing_jobs_url()

        self.assertEqual([], result)
        mock_http_get.assert_called_once_with('/projects/project_name')
        self.assertEqual('Error retrieving pipeline data. Reason: %s.', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], gitlab.GitlabError)

    @patch.object(logging, 'error')
    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_failing_jobs_url_invalid_pipeline_json(self, mock_http_list, mock_http_get, mock_error):
        """ Test the failing jobs urls are empty if there is invalid json of pipeline data. """
        mock_http_list.side_effect = ['non-json']
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.failing_jobs_url()

        self.assertEqual([], result)
        mock_http_get.assert_called_once_with('/projects/project_name')
        self.assertEqual('Error retrieving pipeline data. Reason: %s.', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], AttributeError)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_failing_jobs_url_no_jobs(self, mock_http_list, mock_http_get):
        """ Test the failing jobs urls are empty if there are no failing jobs. """
        mock_http_list.side_effect = [
            [{'id': 123, 'status': 'success', 'web_url': 'https://gitlab.com/pipelines/39'}],
            [{'id': 131, 'status': 'not-failed', 'name': 'job_1', 'web_url': 'https://gitlab.com/jobs-url/'}]]
        mock_http_get.side_effect = [
            {'id': 55, 'name_with_namespace': 'project_name'},
            {'id': 111, 'finished_at': "2018-02-28T13:01:08.8386828Z"}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.failing_jobs_url()

        self.assertEqual([], result)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_unused_jobs_url_success(self, mock_http_list, mock_http_get):
        """ Test that the url of a successful job unused for more than 180 days is returned. """
        mock_http_list.side_effect = [
            [{'id': 123, 'status': 'success', 'web_url': 'https://gitlab.com/pipelines/39'}],
            [{'id': 131, 'status': 'success', 'name': 'job_1', 'web_url': 'https://gitlab.com/jobs-url/'}]]
        mock_http_get.side_effect = [
            {'id': 55, 'name_with_namespace': 'project_name'},
            {'id': 111, 'finished_at': (datetime.datetime.utcnow() - relativedelta(days=181))
                .strftime("%Y-%m-%dT%H:%M:%S.%fZ")}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.unused_jobs_url()

        self.assertEqual([[('project_name / job_1', 'https://gitlab.com/jobs-url/', '181')]], result)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_unused_jobs_url_failed(self, mock_http_list, mock_http_get):
        """ Test that the url of a failing job unused for more than 180 days is returned. """
        mock_http_list.side_effect = [
            [{'id': 123, 'status': 'success', 'web_url': 'https://gitlab.com/pipelines/39'}],
            [{'id': 131, 'status': 'failed', 'name': 'job_1', 'web_url': 'https://gitlab.com/jobs-url/'}]]
        mock_http_get.side_effect = [
            {'id': 55, 'name_with_namespace': 'project_name'},
            {'id': 111, 'finished_at': (datetime.datetime.utcnow() - relativedelta(days=181))
                .strftime("%Y-%m-%dT%H:%M:%S.%fZ")}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.unused_jobs_url()

        self.assertEqual([[('project_name / job_1', 'https://gitlab.com/jobs-url/', '181')]], result)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_number_of_unused_jobs(self, mock_http_list, mock_http_get):
        """ Test that a job unused for less than 180 days is not counted as unused. """
        mock_http_list.side_effect = [
            [{'id': 123, 'status': 'success', 'web_url': 'https://gitlab.com/pipelines/39'}],
            [{'id': 131, 'status': 'failed', 'name': 'job_1', 'web_url': 'https://gitlab.com/jobs-url/'}]]
        mock_http_get.side_effect = [
            {'id': 55, 'name_with_namespace': 'project_name'},
            {'id': 111, 'finished_at': (datetime.datetime.utcnow() - relativedelta(days=179))
                .strftime("%Y-%m-%dT%H:%M:%S.%fZ")}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.number_of_unused_jobs()

        self.assertEqual(0, result)
