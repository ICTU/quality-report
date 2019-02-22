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

import gitlab
from gitlab import Gitlab

from hqlib.metric_source import GitLabCI


class GitLabCITest(unittest.TestCase):
    """ Unit tests for the GitLab class. """

    # pylint: disable=too-many-public-methods

    def setUp(self):
        # pylint: disable=protected-access
        GitLabCI._get_projects.cache_clear()
        GitLabCI._builds_urls.cache_clear()
        GitLabCI._get_built_commits.cache_clear()

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
        last_completed_dt =\
            (datetime.datetime.now().astimezone() - relativedelta(days=5, seconds=4)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_succeeded_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=6)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_completed_status_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_succeeded_status_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S%z")
        mock_http_list.side_effect = [
            [{'id': 123, 'name': 'branch-name-1'}],
            [{'id': 131, 'title': 'Not so cool work', 'created_at': last_completed_dt},
             {'id': 231, 'title': 'Cool feature implemented', 'created_at': last_succeeded_dt}],
            [{'id': 331, 'status': 'failed', 'created_at': last_completed_status_dt, 'commit_id': 131}],
            [{'id': 332, 'status': 'success', 'created_at': last_succeeded_status_dt, 'commit_id': 231}]]
        mock_http_get.side_effect = [
            {'id': 55, 'name': 'project-x', 'path_with_namespace': 'ding-dong/project-x'}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.failing_jobs_url()

        self.assertEqual([
            ('project-x/branch-name-1 - Not so cool work', 'https://gitlab.url.com/ding-dong/project-x/commit/131', 7)
        ], result)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_failing_jobs_url_none_stable_status(self, mock_http_list, mock_http_get):
        """ Test the urls of failing jobs when there are no statuses for stable commit. """
        mock_http_list.side_effect = [
            [{'id': 123, 'name': 'branch-name-1'}],
            [{'id': 131, 'title': 'Not so cool work', 'created_at': 'unimportant'},
             {'id': 231, 'title': 'Cool feature implemented', 'created_at': 'unimportant'}],
            [], [],
            [{'id': 332, 'status': 'success', 'created_at': 'unimportant', 'commit_id': 231}]]
        mock_http_get.side_effect = [
            {'id': 55, 'name': 'project-x', 'path_with_namespace': 'ding-dong/project-x'}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.failing_jobs_url()

        self.assertEqual([], result)

    @patch.object(logging, 'error')
    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_failing_jobs_url_key_error(self, mock_http_list, mock_http_get, mock_error):
        """ Test the urls of failing jobs when the returned json does not contain certain key. """
        mock_http_list.side_effect = [[{'id': 123}]]
        mock_http_get.side_effect = [{'id': 55}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.failing_jobs_url()

        self.assertEqual([], result)
        self.assertEqual('Error retrieving build data. Reason: %s.', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], KeyError)

    @patch.object(logging, 'error')
    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_failing_jobs_url_type_error(self, mock_http_list, mock_http_get, mock_error):
        """ Test the urls of failing jobs when the returned json is invalid. """
        mock_http_list.side_effect = [['---']]
        mock_http_get.side_effect = [{'id': 55}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.failing_jobs_url()

        self.assertEqual([], result)
        self.assertEqual('Error retrieving build data. Reason: %s.', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], TypeError)

    @patch.object(logging, 'error')
    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_failing_jobs_url_list_gitlab_error(self, mock_http_list, mock_http_get, mock_error):
        """ Test the urls of failing jobs when the returned json is invalid. """
        mock_http_list.side_effect = [gitlab.GitlabError]
        mock_http_get.side_effect = [{'id': 55}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.failing_jobs_url()

        self.assertEqual([], result)
        self.assertEqual('Error retrieving build data. Reason: %s.', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], gitlab.GitlabError)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_failing_jobs_url_wrong_statuses(self, mock_http_list, mock_http_get):
        """ Test the urls of failing jobs when there are no success or failure for stable commit. """
        mock_http_list.side_effect = [
            [{'id': 123, 'name': 'branch-name-1'}],
            [{'id': 131, 'title': 'Not so cool work', 'created_at': 'unimportant'},
             {'id': 231, 'title': 'Cool feature implemented', 'created_at': 'unimportant'}],
            [{'status': 'running'}], [{'status': 'whatever'}],
            [{'id': 332, 'status': 'success', 'created_at': 'unimportant', 'commit_id': 231}]]
        mock_http_get.side_effect = [
            {'id': 55, 'name': 'project-x', 'path_with_namespace': 'ding-dong/project-x'}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.failing_jobs_url()

        self.assertEqual([], result)

    @patch.object(logging, 'error')
    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_failing_jobs_url_empty_statuses(self, mock_http_list, mock_http_get, mock_error):
        """ Test the urls of failing jobs when there are no success or failure for stable commit. """
        mock_http_list.side_effect = [
            [{'id': 123, 'name': 'branch-name-1'}],
            [{'id': 131, 'title': 'Not so cool work', 'created_at': 'unimportant'},
             {'id': 231, 'title': 'Cool feature implemented', 'created_at': 'unimportant'}],
            [{}], [{}],
            [{'id': 332, 'status': 'success', 'created_at': 'unimportant', 'commit_id': 231}]]
        mock_http_get.side_effect = [
            {'id': 55, 'name': 'project-x', 'path_with_namespace': 'ding-dong/project-x'}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.failing_jobs_url()

        self.assertEqual([], result)
        self.assertEqual('Error retrieving commit status data. Reason: %s.', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], KeyError)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_failing_jobs_url_filtered_out(self, mock_http_list, mock_http_get):
        """ Test the urls of failing builds where branch name does not match are not considered. """
        mock_http_list.side_effect = [[{'id': 123, 'name': 'branch-name-ONE'}]]
        mock_http_get.side_effect = [{'id': 55, 'project_attributes': 'not-important!'}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name', branch_re=r'\S*-\d')

        result = gitlab_ci.failing_jobs_url()

        self.assertEqual([], result)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_failing_jobs_url_one_day_old(self, mock_http_list, mock_http_get):
        """ Test that the failing urls of projects that built successfully less than a day ago are not counted. """
        last_completed_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=1, seconds=4)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_succeeded_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=6)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_completed_status_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_succeeded_status_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(hours=23, minutes=59)).strftime("%Y-%m-%dT%H:%M:%S%z")
        mock_http_list.side_effect = [
            [{'id': 123, 'name': 'branch-name-1'}],
            [{'id': 131, 'title': 'Not so cool work', 'created_at': last_completed_dt},
             {'id': 231, 'title': 'Cool feature implemented', 'created_at': last_succeeded_dt}],
            [{'id': 331, 'status': 'failed', 'created_at': last_completed_status_dt, 'commit_id': 131}],
            [{'id': 332, 'status': 'success', 'created_at': last_succeeded_status_dt, 'commit_id': 231}]]
        mock_http_get.side_effect = [{'id': 55, 'name': 'project-x', 'path_with_namespace': 'ding-dong/project-x'}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.failing_jobs_url()

        self.assertEqual([], result)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_failing_jobs_url_no_success_commit(self, mock_http_list, mock_http_get):
        """ Test that the time of the last completed commit is taken as relevant if there is no successful one. """
        last_completed_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=5, seconds=4)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_succeeded_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=6)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_completed_status_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%S%z")
        mock_http_list.side_effect = [
            [{'id': 123, 'name': 'branch-name-1'}],
            [{'id': 131, 'title': 'Not so cool work', 'created_at': last_completed_dt},
             {'id': 231, 'title': 'Cool feature implemented', 'created_at': last_succeeded_dt}],
            [{'id': 331, 'status': 'failed', 'created_at': last_completed_status_dt, 'commit_id': 131}],
            [{'status': 'running'}], [{'status': 'whatever'}]]
        mock_http_get.side_effect = [{'id': 55, 'name': 'project-x', 'path_with_namespace': 'ding-dong/project-x'}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.failing_jobs_url()

        self.assertEqual([('project-x/branch-name-1 - Not so cool work',
                           'https://gitlab.url.com/ding-dong/project-x/commit/131', 5)], result)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_number_of_active_jobs(self, mock_http_list, mock_http_get):
        """ Test that the number of active builds is correct. """
        mock_http_list.side_effect = [
            [{'id': 123, 'name': 'branch-name-1'}],
            [{'id': 131, 'title': 'Not so cool work', 'created_at': 'unimportant'},
             {'id': 231, 'title': 'Cool feature implemented', 'created_at': 'unimportant'}],
            [{'id': 331, 'status': 'success', 'created_at': 'unimportant', 'commit_id': 131}],
            [{'id': 332, 'status': 'success', 'created_at': 'unimportant', 'commit_id': 231}]]
        mock_http_get.return_value = {'id': 55, 'name_with_namespace': 'project_name'}
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.number_of_active_jobs()

        self.assertEqual(1, result)

    @patch.object(logging, 'error')
    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_number_of_active_jobs_attribute_error(self, mock_http_list, mock_http_get, mock_error):
        """ Test that the number of active jobs is 0 if error occurred and that it is logged. """
        mock_http_list.side_effect = [AttributeError]
        mock_http_get.return_value = {'id': 55, 'name_with_namespace': 'project_name'}
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name', branch_re=r'\S*_\d')

        result = gitlab_ci.number_of_active_jobs()

        self.assertEqual(0, result)
        self.assertEqual('Error retrieving builds data. Reason: %s.', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], AttributeError)

    @patch.object(logging, 'error')
    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_number_of_active_jobs_gitlab_error(self, mock_http_list, mock_http_get, mock_error):
        """ Test that the number of active jobs is 0 if error occurred and that it is logged. """
        mock_http_list.side_effect = [gitlab.GitlabError]
        mock_http_get.return_value = {'id': 55, 'name_with_namespace': 'project_name'}
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name', branch_re=r'\S*_\d')

        result = gitlab_ci.number_of_active_jobs()

        self.assertEqual(0, result)
        self.assertEqual('Error retrieving builds data. Reason: %s.', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], gitlab.GitlabError)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_number_of_active_jobs_no_project(self, mock_http_list, mock_http_get):
        """ Test that the number of active jobs is correct. """
        gitlab_ci = GitLabCI('https://gitlab.url.com/', *'', branch_re=r'\S*_\d')

        result = gitlab_ci.number_of_active_jobs()

        mock_http_list.assert_not_called()
        mock_http_get.assert_not_called()
        self.assertEqual(0, result)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_number_of_failing_jobs(self, mock_http_list, mock_http_get):
        """ Test the number of failing jobs when there is one. """
        last_completed_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=3, seconds=4)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_succeeded_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=6)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_completed_status_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_succeeded_status_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S%z")
        mock_http_list.side_effect = [
            [{'id': 123, 'name': 'branch-name-1'}],
            [{'id': 131, 'title': 'Not so cool work', 'created_at': last_completed_dt},
             {'id': 231, 'title': 'Cool feature implemented', 'created_at': last_succeeded_dt}],
            [{'id': 331, 'status': 'failed', 'created_at': last_completed_status_dt, 'commit_id': 131}],
            [{'id': 332, 'status': 'success', 'created_at': last_succeeded_status_dt, 'commit_id': 231}]]
        mock_http_get.side_effect = [{'id': 55, 'name': 'project-x', 'path_with_namespace': 'ding-dong/project-x'}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.number_of_failing_jobs()

        self.assertEqual(1, result)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_failing_jobs_url_no_success_builds(self, mock_http_list, mock_http_get):
        """ Test the failing jobs urls are empty if there are no failing builds. """
        last_completed_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=3, seconds=4)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_succeeded_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=6)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_completed_status_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_succeeded_status_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S%z")
        mock_http_list.side_effect = [
            [{'id': 123, 'name': 'branch-name-1'}],
            [{'id': 131, 'title': 'Not so cool work', 'created_at': last_completed_dt},
             {'id': 231, 'title': 'Cool feature implemented', 'created_at': last_succeeded_dt}],
            [{'id': 331, 'status': 'success', 'created_at': last_completed_status_dt, 'commit_id': 131}],
            [{'id': 332, 'status': 'success', 'created_at': last_succeeded_status_dt, 'commit_id': 231}]]
        mock_http_get.side_effect = [{'id': 55, 'name': 'project-x', 'path_with_namespace': 'ding-dong/project-x'}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.failing_jobs_url()

        self.assertEqual([], result)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_unused_jobs_url_success(self, mock_http_list, mock_http_get):
        """ Test that the url of a successful job unused for more than 180 days is returned. """
        last_succeeded_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=181, minutes=5)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_succeeded_status_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=181)).strftime("%Y-%m-%dT%H:%M:%S%z")
        mock_http_list.side_effect = [
            [{'id': 123, 'name': 'branch-name-1'}],
            [{'id': 131, 'title': 'Not so cool work', 'created_at': last_succeeded_dt}],
            [{'id': 331, 'status': 'success', 'created_at': last_succeeded_status_dt, 'commit_id': 131}],
            [{'id': 331, 'status': 'success', 'created_at': last_succeeded_status_dt, 'commit_id': 231}]]
        mock_http_get.side_effect = [{'id': 55, 'name': 'project-x', 'path_with_namespace': 'ding-dong/project-x'}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.unused_jobs_url()

        self.assertEqual([('project-x/branch-name-1 - Not so cool work',
                           'https://gitlab.url.com/ding-dong/project-x/commit/131', 181)], result)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_unused_jobs_url_failed(self, mock_http_list, mock_http_get):
        """ Test that the url of a failing job unused for more than 180 days is returned. """
        last_completed_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=181, seconds=4)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_succeeded_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=200)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_completed_status_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=181)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_succeeded_status_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=200)).strftime("%Y-%m-%dT%H:%M:%S%z")
        mock_http_list.side_effect = [
            [{'id': 123, 'name': 'branch-name-1'}],
            [{'id': 131, 'title': 'Not so cool work', 'created_at': last_completed_dt},
             {'id': 231, 'title': 'Cool feature implemented', 'created_at': last_succeeded_dt}],
            [{'id': 331, 'status': 'failed', 'created_at': last_completed_status_dt, 'commit_id': 131}],
            [{'id': 332, 'status': 'success', 'created_at': last_succeeded_status_dt, 'commit_id': 231}]]
        mock_http_get.side_effect = [{'id': 55, 'name': 'project-x', 'path_with_namespace': 'ding-dong/project-x'}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.unused_jobs_url()

        self.assertEqual([('project-x/branch-name-1 - Not so cool work',
                           'https://gitlab.url.com/ding-dong/project-x/commit/131', 181)], result)

    @patch.object(Gitlab, 'http_get')
    @patch.object(Gitlab, 'http_list')
    def test_number_of_unused_jobs(self, mock_http_list, mock_http_get):
        """ Test that a job unused for less than 180 days is not counted as unused. """
        last_completed_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=179, seconds=4)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_succeeded_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=200)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_completed_status_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=179)).strftime("%Y-%m-%dT%H:%M:%S%z")
        last_succeeded_status_dt = \
            (datetime.datetime.now().astimezone() - relativedelta(days=200)).strftime("%Y-%m-%dT%H:%M:%S%z")
        mock_http_list.side_effect = [
            [{'id': 123, 'name': 'branch-name-1'}],
            [{'id': 131, 'title': 'Not so cool work', 'created_at': last_completed_dt},
             {'id': 231, 'title': 'Cool feature implemented', 'created_at': last_succeeded_dt}],
            [{'id': 331, 'status': 'failed', 'created_at': last_completed_status_dt, 'commit_id': 131}],
            [{'id': 332, 'status': 'success', 'created_at': last_succeeded_status_dt, 'commit_id': 231}]]
        mock_http_get.side_effect = [{'id': 55, 'name': 'project-x', 'path_with_namespace': 'ding-dong/project-x'}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.number_of_unused_jobs()

        self.assertEqual(0, result)

    @patch.object(Gitlab, 'http_get')
    def test_metric_source_urls(self, mock_http_get):
        """ Test if url of metric source is returned correctly."""

        mock_http_get.side_effect = [{'id': 55, 'name': 'project-x', 'web_url': 'http://ding-dong/web_url'}]
        gitlab_ci = GitLabCI('https://gitlab.url.com/', 'project_name')

        result = gitlab_ci.metric_source_urls()

        self.assertEqual(['http://ding-dong/web_url'], result)
