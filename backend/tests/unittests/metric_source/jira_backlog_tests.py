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
from unittest.mock import patch, call
from hqlib.metric_source import JiraFilter, Jira
from hqlib.metric_source.jira_backlog import JiraBacklog, JQL_CONFIG


@patch.object(Jira, 'get_field_id')
@patch.object(Jira, 'get_query')
class JiraBacklogWithLtcsTests(unittest.TestCase):
    """ Unit tests for """
    def test_nr_user_stories_with_sufficient_ltcs(self, mock_get_query, mock_get_field_id):
        """ Tests that the function invokes correct default jql query. """
        mock_get_query.return_value = {"issues": [{"fields": {"custom_123": 1, "issuelinks": [{"id": "1"}]}}]}
        mock_get_field_id.return_value = 'custom_123'
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'custom_field_name')

        result = backlog.nr_user_stories_with_sufficient_ltcs()

        self.assertEqual((1, [{"fields": {"custom_123": 1, "issuelinks": [{"id": "1"}]}}]), result)
        mock_get_field_id.assert_called_once_with('custom_field_name')

    def test_nr_user_stories_with_sufficient_ltcs_multi(self, mock_get_query, mock_get_field_id):
        """ Tests that the function invokes correct default jql query. """
        mock_get_query.side_effect = [{"issues": [{"fields": {"custom_123": 1, "issuelinks": [{"id": "1"}]}}]},
                                      {"issues": [{"fields": {"custom_123": 1, "issuelinks": [{"id": "2"}]}}]}]
        mock_get_field_id.return_value = 'custom_123'
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'custom_field_name',
                              jql_config={"nr_user_stories_with_sufficient_ltcs": ['1st {project}', '2nd {project}']})

        result = backlog.nr_user_stories_with_sufficient_ltcs()

        self.assertEqual((2, [{"fields": {"custom_123": 1, "issuelinks": [{"id": "1"}]}},
                              {"fields": {"custom_123": 1, "issuelinks": [{"id": "2"}]}}]), result)
        mock_get_field_id.assert_called_once_with('custom_field_name')
        self.assertEqual([call('1st project!'), call('2nd project!')], mock_get_query.call_args_list)

    def test_nr_user_stories_with_sufficient_ltcs_error(self, mock_get_query, mock_get_field_id):
        """ Tests that the function invokes correct default jql query. """
        mock_get_field_id.return_value = None
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'custom_field_name')

        result = backlog.nr_user_stories_with_sufficient_ltcs()

        self.assertEqual((-1, []), result)
        mock_get_field_id.assert_called_once_with('custom_field_name')
        mock_get_query.assert_not_called()

    @patch.object(logging, 'error')
    def test_nr_user_stories_with_sufficient_ltcs_field(self, mock_error, mock_get_query, mock_get_field_id):
        """ Tests that the function invokes correct default jql query. """
        mock_get_query.return_value = {"issues": [{"fields": {"issuelinks": [{"id": "1"}]}}]}
        mock_get_field_id.return_value = 'missing_custom_field'
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'custom_field_name')

        result = backlog.nr_user_stories_with_sufficient_ltcs()

        self.assertEqual((-1, []), result)
        mock_get_field_id.assert_called_once_with('custom_field_name')
        self.assertEqual('Error processing jira response. The key %s not found!', mock_error.call_args_list[0][0][0])
        self.assertIsInstance(mock_error.call_args_list[0][0][1], KeyError)


@patch.object(JiraFilter, 'nr_issues')
class JiraBacklogTests(unittest.TestCase):
    """ Unit tests of the constructor of the Jira class. """

    # pylint: disable=too-many-public-methods

    @patch.object(JiraFilter, '__init__')
    def test_init(self, mock_init, mock_nr_issues):
        """ Tests that the inner JiraFilter is initialized with correct parameters """
        mock_init.return_value = None
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'unimportant')
        backlog.nr_user_stories()
        mock_nr_issues.assert_called_once()
        mock_init.assert_called_once_with('url!', 'username!', 'password!')
        self.assertEqual('Jira backlog', backlog.metric_source_name)

    def test_nr_user_stories(self, mock_nr_issues):
        """ Tests that the function invokes correct default jql query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'unimportant')
        result = backlog.nr_user_stories()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once_with('project = "project!" AND type = Story')

    def test_nr_user_stories_custom(self, mock_nr_issues):
        """ Tests that the function invokes correct custom jql query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'unimportant',
                              jql_config={"nr_user_stories": ['1st {project}', '2nd {project}']})
        result = backlog.nr_user_stories()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once_with('1st project!', '2nd project!')

    def test_nr_user_stories_custom_filter_number(self, mock_nr_issues):
        """ Tests that the function invokes correct custom jira filter number instead of the query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'whatever!?', 'unimportant',
                              jql_config={"nr_user_stories": [11, '12']})
        result = backlog.nr_user_stories()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once_with('11', '12')

    def test_approved_user_stories(self, mock_nr_issues):
        """ Tests that the function invokes correct default jql query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'unimportant')
        result = backlog.approved_user_stories()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once()

    def test_approved_user_stories_custom(self, mock_nr_issues):
        """ Tests that the function invokes correct custom jql query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'unimportant',
                              jql_config={"approved_user_stories": ['1st {project}', '2nd {project}']})
        result = backlog.approved_user_stories()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once_with('1st project!', '2nd project!')

    def test_approved_user_stories_custom_filter_number(self, mock_nr_issues):
        """ Tests that the function invokes correct custom jira filter number instead of the query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'whatever!?', 'unimportant',
                              jql_config={"approved_user_stories": [11, '12']})
        result = backlog.approved_user_stories()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once_with('11', '12')

    def test_reviewed_user_stories(self, mock_nr_issues):
        """ Tests that the function invokes correct default jql query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'unimportant')
        result = backlog.reviewed_user_stories()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once()

    def test_reviewed_user_stories_custom(self, mock_nr_issues):
        """ Tests that the function invokes correct custom jql query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'unimportant',
                              jql_config={"reviewed_user_stories": ['1st {project}', '2nd {project}']})
        result = backlog.reviewed_user_stories()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once_with('1st project!', '2nd project!')

    def test_reviewed_user_stories_custom_filter_number(self, mock_nr_issues):
        """ Tests that the function invokes correct custom jira filter number instead of the query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'whatever!?', 'unimportant',
                              jql_config={"reviewed_user_stories": [11, '12']})
        result = backlog.reviewed_user_stories()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once_with('11', '12')

    def test_reviewed_ltcs(self, mock_nr_issues):
        """ Tests that the function invokes correct default jql query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'unimportant')
        result = backlog.reviewed_ltcs()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once()

    def test_reviewed_ltcs_custom(self, mock_nr_issues):
        """ Tests that the function invokes correct custom jql query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'unimportant',
                              jql_config={"reviewed_ltcs": ['1st {project}', '2nd {project}']})
        result = backlog.reviewed_ltcs()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once_with('1st project!', '2nd project!')

    def test_reviewed_ltcs_custom_filter_number(self, mock_nr_issues):
        """ Tests that the function invokes correct custom jira filter number instead of the query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'whatever!?', 'unimportant',
                              jql_config={"reviewed_ltcs": [11, '12']})
        result = backlog.reviewed_ltcs()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once_with('11', '12')

    def test_nr_ltcs(self, mock_nr_issues):
        """ Tests that the function invokes correct default jql query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'unimportant')
        result = backlog.nr_ltcs()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once()

    def test_nr_ltcs_custom(self, mock_nr_issues):
        """ Tests that the function invokes correct custom jql query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'unimportant',
                              jql_config={"nr_ltcs": ['1st {project}', '2nd {project}']})
        result = backlog.nr_ltcs()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once_with('1st project!', '2nd project!')

    def test_nr_ltcs_custom_filter_number(self, mock_nr_issues):
        """ Tests that the function invokes correct custom jira filter number instead of the query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'whatever!?', 'unimportant',
                              jql_config={"nr_ltcs": [11, '12']})
        result = backlog.nr_ltcs()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once_with('11', '12')

    def test_approved_ltcs(self, mock_nr_issues):
        """ Tests that the function invokes correct default jql query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'unimportant')
        result = backlog.approved_ltcs()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once()

    def test_approved_ltcs_custom(self, mock_nr_issues):
        """ Tests that the function invokes correct custom jql query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'unimportant',
                              jql_config={"approved_ltcs": ['1st {project}', '2nd {project}']})
        result = backlog.approved_ltcs()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once_with('1st project!', '2nd project!')

    def test_approved_ltcs_custom_filter_number(self, mock_nr_issues):
        """ Tests that the function invokes correct custom jira filter number instead of the query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'whatever!?', 'unimportant',
                              jql_config={"approved_ltcs": [11, '12']})
        result = backlog.approved_ltcs()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once_with('11', '12')

    def test_nr_automated_ltcs(self, mock_nr_issues):
        """ Tests that the function invokes correct default jql query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'unimportant')
        result = backlog.nr_automated_ltcs()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once()

    def test_nr_automated_ltcs_custom(self, mock_nr_issues):
        """ Tests that the function invokes correct custom jql query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'unimportant',
                              jql_config={"nr_automated_ltcs": ['1st {project}', '2nd {project}']})
        result = backlog.nr_automated_ltcs()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once_with('1st project!', '2nd project!')

    def test_nr_automated_ltcs_custom_filter_number(self, mock_nr_issues):
        """ Tests that the function invokes correct custom jira filter number instead of the query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'whatever!?', 'unimportant',
                              jql_config={"nr_automated_ltcs": [11, '12']})
        result = backlog.nr_automated_ltcs()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once_with('11', '12')

    def test_nr_ltcs_to_be_automated(self, mock_nr_issues):
        """ Tests that the function invokes correct default jql query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'unimportant')
        result = backlog.nr_ltcs_to_be_automated()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once()

    def test_nr_ltcs_to_be_automated_custom(self, mock_nr_issues):
        """ Tests that the function invokes correct custom jql query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'unimportant',
                              jql_config={"nr_ltcs_to_be_automated": ['1st {project}', '2nd {project}']})
        result = backlog.nr_ltcs_to_be_automated()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once_with('1st project!', '2nd project!')

    def test_nr_ltcs_to_be_automated_custom_filter_number(self, mock_nr_issues):
        """ Tests that the function invokes correct custom jira filter number instead of the query. """
        mock_nr_issues.return_value = 1, ['a']
        backlog = JiraBacklog('url!', 'username!', 'password!', 'whatever!?', 'unimportant',
                              jql_config={"nr_ltcs_to_be_automated": [11, '12']})
        result = backlog.nr_ltcs_to_be_automated()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once_with('11', '12')

    def test_nr_manual_ltcs(self, mock_nr_issues):
        """ Tests that the function invokes correct custom jira filter number instead of the query. """
        backlog = JiraBacklog('url!', 'username!', 'password!', 'Project Name', 'unimportant')
        mock_nr_issues.return_value = 1, ['a']
        result = backlog.nr_manual_ltcs()
        self.assertEqual((1, ['a']), result)
        mock_nr_issues.assert_called_once_with(JQL_CONFIG["nr_manual_ltcs"].format(project='Project Name'))


class JiraBacklogPlaceholdersTests(unittest.TestCase):
    """ Unit tests for dummy functions """

    def test_metric_source_urls(self):
        """ Tests that the function correctly formats display url. """
        backlog = JiraBacklog('http://url', 'username!', 'password!', 'whatever!?', 'unimportant')
        self.assertEqual(['http://url/issues/?jql=key%20in%20(issue-1)'], backlog.metric_source_urls('issue-1'))

    def test_metric_source_urls_many_issues(self):
        """ Tests that the function correctly formats display url. """
        backlog = JiraBacklog('http://url', 'username!', 'password!', 'whatever!?', 'unimportant')
        self.assertEqual(['http://url/issues/?jql=key%20in%20(issue-1%2Cissue-2)'],
                         backlog.metric_source_urls('issue-1', 'issue-2'))

    def test_date_of_last_manual_test(self):
        """ Tests that the function invokes correct custom jira filter number instead of the query. """
        backlog = JiraBacklog('url!', 'username!', 'password!', 'whatever!?', 'unimportant')
        self.assertEqual(datetime.datetime.min, backlog.date_of_last_manual_test())

    def test_manual_test_execution_url(self):
        """ Tests that the function invokes correct custom jira filter number instead of the query. """
        backlog = JiraBacklog('url!', 'username!', 'password!', 'whatever!?', 'unimportant')
        self.assertEqual('', backlog.manual_test_execution_url())

    def test_nr_manual_ltcs_too_old(self):
        """ Tests that the function invokes correct default jql query. """
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'unimportant')
        self.assertEqual(-1, backlog.nr_manual_ltcs_too_old('1', 1))

    def test_nr_manual_ltcs_too_old_custom(self):
        """ Tests that the function invokes correct custom jql query. """
        backlog = JiraBacklog('url!', 'username!', 'password!', 'project!', 'unimportant')
        self.assertEqual(-1, backlog.nr_manual_ltcs_too_old('1', 1))

    def test_nr_manual_ltcs_too_old_custom_filter_number(self):
        """ Tests that the function invokes correct custom jira filter number instead of the query. """
        backlog = JiraBacklog('url!', 'username!', 'password!', 'whatever!?', 'unimportant')
        self.assertEqual(-1, backlog.nr_manual_ltcs_too_old('1', 1))
