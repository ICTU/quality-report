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
from unittest.mock import MagicMock, patch, call
import logging

from hqlib import metric, domain, metric_source
from .bug_metrics_tests import FakeJiraFilter


class ProjectPrerequisitesTestCase(unittest.TestCase):
    """ Prerequisites tests for UserStoriesDurationTest and UserStoriesInProgress"""

    def test_project_for_user_stories_in_progress(self):
        """ Checks if the real objects fulfill requirements expected by LastSecurityTestCase """

        project = domain.Project()

        self.assertTrue(project is not None)
        self.assertTrue(callable(getattr(project, "metric_sources")))
        self.assertTrue(callable(getattr(project, "metric_source_id")))


class ReadyUserStoryPointsTest(unittest.TestCase):
    """ Unit tests for the number of ready user story points metric. """

    def setUp(self):
        self.__project = unittest.mock.create_autospec(domain.Project, instance=True)
        self.__subject = MagicMock()
        self.__subject.metric_source_id.return_value = "src_id"

    def test_norm(self):
        """ Test that the norm is correct. """
        self.__subject.target.return_value = 20
        self.__subject.low_target.return_value = 10
        duration_metric = metric.ReadyUserStoryPoints(project=self.__project, subject=self.__subject)

        self.assertEqual("Minimaal 20 ready user story punten. "
                         "Minder dan 10 ready user story punten is rood.", duration_metric.norm())

    @patch.object(metric_source.JiraFilter, 'issues_with_field')
    def test_value(self, issues_with_field_mock):
        """ Test that the sum value is calculated correctly. """
        jira_filter = metric_source.JiraFilter('http://jira/', 'username', 'password')
        issues_with_field_mock.return_value = [("issue1", 50), ("issue2", 70)]
        self.__project = domain.Project(metric_sources={metric_source.ReadyUserStoryPointsTracker: jira_filter},
                                        metric_source_ids={jira_filter: '12345'})
        ready_metric = metric.ReadyUserStoryPoints(project=self.__project, subject=self.__subject)

        issues_with_field_mock.asses_called_once()
        self.assertEqual(120, ready_metric.value())


class UserStoriesDurationTest(unittest.TestCase):
    """ Unit tests for duration of user stories. """

    def setUp(self):
        self.__project = unittest.mock.create_autospec(domain.Project, instance=True)
        self.__subject = MagicMock()
        self.__subject.metric_source_id.return_value = "src_id"

    @patch.object(metric_source.Jira, 'get_issue_details')
    @patch.object(metric_source.Jira, 'get_query')
    def test_get_duration_of_stories(self, get_issues_mock, get_issue_details_mock):
        """ Test that the average number of days a story spent in status 'In Progress' is correct. """
        issue = "ISSUE-1"
        issue2 = "ISSUE-2"
        jira_filter = metric_source.JiraFilter('http://jira/', 'username', 'password')
        issues_json = {"total": "5", "issues": [{"key": issue, "fields": {"summary": "Issue Title"}},
                                                {"key": issue2, "fields": {"summary": "Issue2 Title"}}]}
        changelog_json = {
            "id": "133274",
            "changelog": {
                "histories": [
                    {
                        "created": "2017-12-15T23:54:15.000+0100",
                        "items": [
                            {"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]},
                    {
                        "created": "2017-11-15T23:54:15.000+0100",
                        "items": [
                            {"field": "Flagged", "fieldtype": "custom", "fromString": "X", "toString": "X"}]},
                    {
                        "created": "2017-12-25T09:59:15.000+0100",
                        "items": [
                            {"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}]}}
        changelog_json2 = {
            "id": "133274",
            "changelog": {
                "histories": [
                    {
                        "created": "2017-11-15T08:54:15.000+0100",
                        "items": [{"field": "status", "fieldtype": "jira", "fromString": "X", "toString":
                                   "In Progress"}]},
                    {
                        "created": "2017-11-16T09:59:15.000+0100",
                        "items": [
                            {"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}]}}
        get_issues_mock.return_value = issues_json
        get_issue_details_mock.side_effect = [changelog_json, changelog_json2]
        self.__project.metric_sources.return_value = [jira_filter]
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        result = duration_metric.value()

        get_issues_mock.assert_called_once()
        get_issue_details_mock.assert_has_calls([call(issue), call(issue2)])
        self.assertEqual(5, result)

    @patch.object(metric.UserStoriesDuration, '_get_days_in_progress')
    @patch.object(domain.Metric, '_get_metric_source_ids')
    @patch.object(metric_source.JiraFilter, 'sum_for_all_issues')
    def test_get_duration_of_stories_more_sources(self, sum_for_all_issues_mock,
                                                  get_metric_source_ids_mock, get_days_in_progress_mock):
        """ Test that the average number of days calls is summed for all metric source ids. """
        jira_filter = metric_source.JiraFilter('http://jira/', 'username', 'password')
        self.__project.metric_sources.return_value = [jira_filter]
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)
        get_metric_source_ids_mock.return_value = ['1522', '1255']

        duration_metric.value()

        get_metric_source_ids_mock.assert_called_once()
        sum_for_all_issues_mock.assert_has_calls(
            [call('1522', get_days_in_progress_mock, []),
             call('1255', get_days_in_progress_mock, [])])

    @patch.object(domain.Metric, '_get_metric_source_ids')
    @patch.object(metric_source.JiraFilter, 'sum_for_all_issues')
    def test_get_duration_sum_value_error(self, sum_for_all_issues_mock, get_metric_source_ids_mock):
        """ Test that the average number of days calls is summed for all metric source ids. """
        jira_filter = metric_source.JiraFilter('http://jira/', 'username', 'password')
        self.__project.metric_sources.return_value = [jira_filter]
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)
        get_metric_source_ids_mock.return_value = ['1522']
        sum_for_all_issues_mock.side_effect = [ValueError]

        result = duration_metric.value()

        get_metric_source_ids_mock.assert_called_once()
        sum_for_all_issues_mock.assert_called_once()
        self.assertEqual(-1, result)

    @patch.object(metric_source.Jira, 'get_issue_details')
    @patch.object(metric_source.Jira, 'get_query')
    def test_extra_info_duration_of_stories_ok(self, get_issues_mock, get_issue_details_mock):
        """ Test that the content of extra info for a story is correct. """
        issue = "ISSUE-1"
        jira_filter = metric_source.JiraFilter('http://jira/', 'username', 'password')
        issues_json = {"total": "5", "issues": [{"key": issue, "fields": {"summary": "Issue Title"}}]}
        changelog_json = {
            "id": "133274",
            "changelog": {
                "histories": [
                    {
                        "created": "2017-12-15T23:54:15.000+0100",
                        "items": [{"field": "status", "fieldtype": "jira", "fromString": "X",
                                   "toString": "In Progress"}]},
                    {
                        "created": "2017-11-15T23:54:15.000+0100",
                        "items": [{"field": "Flagged", "fieldtype": "custom", "fromString": "X", "toString": "X"}]},
                    {
                        "created": "2017-12-25T09:59:15.000+0100",
                        "items": [{"field": "status", "fieldtype": "jira", "fromString": "In Progress",
                                   "toString": "X"}]}]}}
        get_issues_mock.return_value = issues_json
        get_issue_details_mock.return_value = changelog_json
        self.__project.metric_sources.return_value = [jira_filter]
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        duration_metric.value()

        result = duration_metric.extra_info()

        get_issues_mock.assert_called_once()
        get_issue_details_mock.assert_has_calls([call(issue)])
        self.assertEqual('15 december 2017', result.data[0]['day_in'])
        self.assertEqual('25 december 2017', result.data[0]['day_out'])
        self.assertEqual(False, result.data[0]['is_omitted'])
        self.assertEqual(9, result.data[0]['days'])

    @patch.object(metric_source.Jira, 'get_issue_details')
    @patch.object(metric_source.Jira, 'get_query')
    def testvalue_extra_info_stories_still_in_progress(self, get_issues_mock, get_issue_details_mock):
        """ Test that the content of extra info for a story still in progress is correct. """
        issue = "ISSUE-1"
        jira_filter = metric_source.JiraFilter('http://jira/', 'username', 'password')
        issues_json = {"total": "5", "issues": [{"key": issue, "fields": {"summary": "Issue Title"}}]}
        changelog_json = {
            "id": "133274",
            "changelog": {
                "histories": [
                    {
                        "created": "2017-12-15T23:54:15.000+0100",
                        "items": [{"field": "status", "fieldtype": "jira", "fromString": "X",
                                   "toString": "In Progress"}]}]}}
        get_issues_mock.return_value = issues_json
        get_issue_details_mock.return_value = changelog_json
        self.__project.metric_sources.return_value = [jira_filter]
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        duration_metric.value()
        result = duration_metric.extra_info()

        get_issues_mock.assert_called_once()
        get_issue_details_mock.assert_has_calls([call(issue)])
        self.assertEqual('15 december 2017', result.data[0]['day_in'])
        self.assertEqual('geen', result.data[0]['day_out'])
        self.assertEqual(True, result.data[0]['is_omitted'])
        self.assertEqual('n.v.t', result.data[0]['days'])

    @patch.object(metric_source.Jira, 'get_issue_details')
    @patch.object(metric_source.Jira, 'get_query')
    def testvalue_extra_info_stories_never_in_progress(self, get_issues_mock, get_issue_details_mock):
        """ Test that the content of extra info for a story that never got in progress contains no dates. """
        issue = "ISSUE-1"
        jira_filter = metric_source.JiraFilter('http://jira/', 'username', 'password')
        issues_json = {"total": "5", "issues": [{"key": issue, "fields": {"summary": "Issue Title"}}]}
        changelog_json = {
            "id": "133274",
            "changelog": {
                "histories": [
                    {
                        "created": "2017-12-15T23:54:15.000+0100",
                        "items": [{"field": "Flagged", "fieldtype": "custom", "fromString": "X",
                                   "toString": "X"}]}]}}
        get_issues_mock.return_value = issues_json
        get_issue_details_mock.side_effect = [changelog_json]
        self.__project.metric_sources.return_value = [jira_filter]
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        duration_metric.value()
        result = duration_metric.extra_info()

        get_issues_mock.assert_called_once()
        get_issue_details_mock.assert_has_calls([call(issue)])
        self.assertEqual('geen', result.data[0]['day_in'])
        self.assertEqual('geen', result.data[0]['day_out'])
        self.assertEqual(True, result.data[0]['is_omitted'])
        self.assertEqual('n.v.t', result.data[0]['days'])

    @patch.object(metric_source.Jira, 'get_issue_details')
    @patch.object(metric_source.Jira, 'get_query')
    def testvalue_extra_info_duration_of_more_stories(self, get_issues_mock, get_issue_details_mock):
        """ Test that the content of extra info for multiple stories is correct. """
        issue = "ISSUE-1"
        issue2 = "ISSUE-2"
        jira_filter = metric_source.JiraFilter('http://jira/', 'username', 'password')
        issues_json = {"total": "5", "issues": [{"key": issue, "fields": {"summary": "Issue Title"}},
                                                {"key": issue2, "fields": {"summary": "Issue2 Title"}}]}
        changelog_json = {
            "id": "133274",
            "changelog": {
                "histories": [
                    {
                        "created": "2017-12-15T23:54:15.000+0100",
                        "items": [{"field": "status", "fieldtype": "jira", "fromString": "X",
                                   "toString": "In Progress"}]},
                    {
                        "created": "2017-11-15T23:54:15.000+0100",
                        "items": [{"field": "Flagged", "fieldtype": "custom", "fromString": "X", "toString": "X"}]},
                    {
                        "created": "2017-12-25T09:59:15.000+0100",
                        "items": [
                            {"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}]}}
        changelog_json2 = {
            "id": "133274",
            "changelog": {
                "histories": [
                    {
                        "created": "2017-11-15T08:54:15.000+0100",
                        "items": [
                            {"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]},
                    {
                        "created": "2017-11-16T09:59:15.000+0100",
                        "items": [
                            {"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}]}}
        get_issues_mock.return_value = issues_json
        get_issue_details_mock.side_effect = [changelog_json, changelog_json2]
        self.__project.metric_sources.return_value = [jira_filter]
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        duration_metric.value()
        result = duration_metric.extra_info()

        get_issues_mock.assert_called_once()
        get_issue_details_mock.assert_has_calls([call(issue), call(issue2)])
        self.assertEqual('15 december 2017', result.data[0]['day_in'])
        self.assertEqual('25 december 2017', result.data[0]['day_out'])
        self.assertEqual(9, result.data[0]['days'])
        self.assertEqual('15 november 2017', result.data[1]['day_in'])
        self.assertEqual('16 november 2017', result.data[1]['day_out'])
        self.assertEqual(1, result.data[1]['days'])

    @patch.object(metric_source.Jira, 'get_issue_details')
    @patch.object(metric_source.Jira, 'get_query')
    def testvalue_get_duration_of_stories_with_changes(self, get_issues_mock, get_issue_details_mock):
        """ Test that the number of days from the first enter in status 'In Progress' till the last exit of it
        is correct for multiple status changes. """
        issue = "ISSUE-1"
        jira_filter = metric_source.JiraFilter('http://jira/', 'username', 'password')
        issues_json = {"total": "5", "issues": [{"key": issue, "fields": {"summary": "Issue Title"}}]}
        changelog_json = {"id": "133274", "changelog": {"histories": [
            {"created": "2017-12-15T23:54:15.000+0100", "items": [
                {"field": "status", "fieldtype": "jira", "fromString": "Op", "toString": "In Progress"}]},
            {"created": "2017-12-16T10:54:15.000+0100", "items": [
                {"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]},
            {"created": "2017-12-16T23:52:15.000+0100", "items": [
                {"field": "status", "fieldtype": "jira", "fromString": "RO", "toString": "In Progress"}]},
            {"created": "2017-12-25T09:59:15.000+0100", "items": [
                {"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}]}}
        get_issues_mock.return_value = issues_json
        get_issue_details_mock.side_effect = [changelog_json]
        self.__project.metric_sources.return_value = [jira_filter]
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        result = duration_metric.value()

        get_issues_mock.assert_called_once()
        get_issue_details_mock.assert_has_calls([call(issue)])
        self.assertEqual(9, result)

    @patch.object(logging, 'info')
    @patch.object(metric_source.Jira, 'get_issue_details')
    @patch.object(metric_source.Jira, 'get_query')
    def testvalue_get_duration_never_got_in_progress_single(self, get_issues_mock, get_issue_details_mock,
                                                            logging_info_mock):
        """ Test that the number of days returned is -1 if a single story never entered the state "In Progress". """
        issue = "ISSUE-1"
        jira_filter = metric_source.JiraFilter('http://jira/', 'username', 'password')
        issues_json = {"total": "5", "issues": [{"key": issue, "fields": {"summary": "Issue Title"}}]}
        changelog_json = {"id": "133274", "changelog": {"histories": [
            {"created": "2017-12-15T23:54:15.000+0100", "items": [
                {"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "Open"}]}]}}
        get_issues_mock.return_value = issues_json
        get_issue_details_mock.side_effect = [changelog_json]
        self.__project.metric_sources.return_value = [jira_filter]
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        result = duration_metric.value()

        logging_info_mock.assert_called_with(
            "Invalid date, or issue %s never moved to status 'In Progress'", issue)
        get_issues_mock.assert_called_once()
        get_issue_details_mock.assert_has_calls([call(issue)])
        self.assertEqual(-1, result)

    @patch.object(logging, 'info')
    @patch.object(metric_source.Jira, 'get_issue_details')
    @patch.object(metric_source.Jira, 'get_query')
    def testvalue_get_duration_that_never_got_in_progress(self, get_issues_mock, get_issue_details_mock,
                                                          logging_info_mock):
        """ Test that story never entered the state "In Progress" does not influence calculated average. """
        issue = "ISSUE-1"
        issue2 = "ISSUE-2"
        jira_filter = metric_source.JiraFilter('http://jira/', 'username', 'password')
        issues_json = {"total": "5", "issues": [
            {"key": issue, "fields": {"summary": "Issue Title"}},
            {"key": issue2, "fields": {"summary": "Issue2 Title"}}]}
        changelog_json = {"id": "133274", "changelog": {"histories": [
            {"created": "2017-12-15T23:54:15.000+0100", "items": [
                {"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "Open"}]}]}}
        changelog_json2 = {"id": "133274", "changelog": {"histories": [
            {"created": "2017-12-15T23:54:15.000+0100", "items": [
                {"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]},
            {"created": "2017-12-25T09:59:15.000+0100", "items": [
                {"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}]}}
        get_issues_mock.return_value = issues_json
        get_issue_details_mock.side_effect = [changelog_json, changelog_json2]
        self.__project.metric_sources.return_value = [jira_filter]
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        result = duration_metric.value()

        logging_info_mock.assert_called_with(
            "Invalid date, or issue %s never moved to status 'In Progress'", issue)
        get_issues_mock.assert_called_once()
        get_issue_details_mock.assert_has_calls([call(issue), call(issue2)])
        self.assertEqual(9, result)

    @patch.object(logging, 'info')
    @patch.object(metric_source.Jira, 'get_issue_details')
    @patch.object(metric_source.Jira, 'get_query')
    def testvalue_get_duration_still_in_progress_single(self, get_issues_mock, get_issue_details_mock,
                                                        logging_info_mock):
        """ Test that the number of days returned is -1 if a story is still in state "In Progress". """
        issue = "ISSUE-1"
        jira_filter = metric_source.JiraFilter('http://jira/', 'username', 'password')
        issues_json = {"total": "5", "issues": [{"key": issue, "fields": {"summary": "Issue Title"}}]}
        changelog_json = {"id": "133274", "changelog": {"histories": [
            {"created": "2017-12-15T23:54:15.000+0100", "items": [
                {"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]}]}}
        get_issues_mock.return_value = issues_json
        get_issue_details_mock.return_value = changelog_json
        self.__project.metric_sources.return_value = [jira_filter]
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        result = duration_metric.value()

        logging_info_mock.assert_called_with(
            "Invalid date, or issue %s still in status 'In Progress'", issue)
        get_issues_mock.assert_called_once()
        get_issue_details_mock.assert_has_calls([call(issue)])
        self.assertEqual(-1, result)

    @patch.object(logging, 'info')
    @patch.object(metric_source.Jira, 'get_issue_details')
    @patch.object(metric_source.Jira, 'get_query')
    def testvalue_get_duration_of_stories_still_in_progress(self, get_issues_mock,
                                                            get_issue_details_mock, logging_info_mock):
        """ Test that a story that is still in state "In Progress" does not influence calculated average. """
        issue = "ISSUE-1"
        issue2 = "ISSUE-2"
        jira_filter = metric_source.JiraFilter('http://jira/', 'username', 'password')
        issues_json = {"total": "5", "issues": [{"key": issue, "fields": {"summary": "Issue Title"}},
                                                {"key": issue2, "fields": {"summary": "Issue2 Title"}}]}
        changelog_json = {"id": "133274", "changelog": {"histories": [
            {"created": "2017-12-15T23:54:15.000+0100", "items": [
                {"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]}]}}
        changelog_json2 = {"id": "133274", "changelog": {"histories": [
            {"created": "2017-12-15T23:54:15.000+0100", "items": [
                {"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]},
            {"created": "2017-12-25T09:59:15.000+0100", "items": [
                {"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}]}}
        get_issues_mock.return_value = issues_json
        get_issue_details_mock.side_effect = [changelog_json, changelog_json2]
        self.__project.metric_sources.return_value = [jira_filter]
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        result = duration_metric.value()

        logging_info_mock.assert_called_with(
            "Invalid date, or issue %s still in status 'In Progress'", issue)
        get_issues_mock.assert_called_once()
        get_issue_details_mock.assert_has_calls([call(issue), call(issue2)])
        self.assertEqual(9, result)

    @patch.object(logging, 'info')
    @patch.object(metric_source.Jira, 'get_issue_details')
    @patch.object(metric_source.Jira, 'get_query')
    def testvalue_get_duration_of_stories_invalid_to_date(self, get_issues_mock, get_issue_details_mock,
                                                          logging_info_mock):
        """ Test that the number of days returned is -1 for a story that has invalid date of progress start. """
        issue = "ISSUE-1"
        jira_filter = metric_source.JiraFilter('http://jira/', 'username', 'password')
        issues_json = {"total": "5", "issues": [{"key": issue, "fields": {"summary": "Issue Title"}}]}
        changelog_json = {"id": "133274", "changelog": {"histories": [
            {"created": "2017-33-15T23:54:15.000+0100", "items": [
                {"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]},
            {"created": "2017-11-15T23:54:15.000+0100", "items": [
                {"field": "Flagged", "fieldtype": "custom", "fromString": "X", "toString": "X"}]},
            {"created": "2017-12-25T09:59:15.000+0100", "items": [
                {"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}]}}
        get_issues_mock.return_value = issues_json
        get_issue_details_mock.return_value = changelog_json
        self.__project.metric_sources.return_value = [jira_filter]
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        result = duration_metric.value()

        logging_info_mock.assert_called_with(
            "Invalid date, or issue %s never moved to status 'In Progress'", issue)
        get_issues_mock.assert_called_once()
        get_issue_details_mock.assert_has_calls([call(issue)])
        self.assertEqual(-1, result)

    @patch.object(logging, 'info')
    @patch.object(metric_source.Jira, 'get_issue_details')
    @patch.object(metric_source.Jira, 'get_query')
    def testvalue_get_duration_of_stories_invalid_from_date(self, get_issues_mock,
                                                            get_issue_details_mock, logging_info_mock):
        """ Test that the number of days returned is -1 for a a story that has invalid date of progress end. """
        issue = "ISSUE-1"
        jira_filter = metric_source.JiraFilter('http://jira/', 'username', 'password')
        issues_json = {"total": "5", "issues": [{"key": issue, "fields": {"summary": "Issue Title"}}]}
        changelog_json = {"id": "133274", "changelog": {"histories": [
            {"created": "2017-12-15T23:54:15.000+0100", "items": [
                {"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]},
            {"created": "2017-22-25T09:59:15.000+0100", "items": [
                {"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}]}}
        get_issues_mock.return_value = issues_json
        get_issue_details_mock.return_value = changelog_json
        self.__project.metric_sources.return_value = [jira_filter]
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        result = duration_metric.value()

        logging_info_mock.assert_called_with(
            "Invalid date, or issue %s still in status 'In Progress'", issue)
        get_issues_mock.assert_called_once()
        get_issue_details_mock.assert_has_calls([call(issue)])
        self.assertEqual(-1, result)

    @patch.object(logging, 'error')
    @patch.object(metric_source.Jira, 'get_issue_details')
    @patch.object(metric_source.Jira, 'get_query')
    def testvalue_get_duration_of_stories_json_error(self, get_issues_mock, get_issue_details_mock, logging_mock):
        """ Test that the number of days returned is -1 if an invalid json is returned as a result. """
        issue = "ISSUE-1"
        jira_filter = metric_source.JiraFilter('http://jira/', 'username', 'password')
        issues_json = {"total": "5", "issues": [{"key": issue, "fields": {"summary": "Issue Title"}}]}
        changelog_json = 'not a json'
        get_issues_mock.return_value = issues_json
        get_issue_details_mock.side_effect = [changelog_json]
        self.__project.metric_sources.return_value = [jira_filter]
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        result = duration_metric.value()

        logging_mock.assert_called_with("Received invalid json from %s: %s", "http://jira/", changelog_json)
        get_issues_mock.assert_called_once()
        get_issue_details_mock.assert_has_calls([call(issue)])
        self.assertEqual(-1, result)

    @patch.object(metric_source.Jira, 'get_issue_details')
    @patch.object(metric_source.Jira, 'get_query')
    def test_report(self, get_issues_mock, get_issue_details_mock):
        """ Test that the report is correct. """
        issue = "ISSUE-1"
        jira_filter = metric_source.JiraFilter('http://jira/', 'username', 'password')
        issues_json = {"total": "5", "issues": [{"key": issue, "fields": {"summary": "Issue Title"}}]}
        changelog_json = {
            "id": "133274",
            "changelog": {
                "histories": [
                    {
                        "created": "2017-12-15T23:54:15.000+0100",
                        "items": [
                            {"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]},
                    {
                        "created": "2017-11-15T23:54:15.000+0100",
                        "items": [
                            {"field": "Flagged", "fieldtype": "custom", "fromString": "X", "toString": "X"}]},
                    {
                        "created": "2017-12-25T09:59:15.000+0100",
                        "items": [
                            {"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}]}}
        get_issues_mock.return_value = issues_json
        get_issue_details_mock.return_value = changelog_json
        self.__project.metric_sources.return_value = [jira_filter]
        self.__subject.metric_source_id.return_value = 3
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        self.assertEqual("5 user stories waren 9.0 dagen gemiddeld in progress.", duration_metric.report())

    def test_norm(self):
        """ Test that the norm is correct. """
        self.__subject.target.return_value = 5
        self.__subject.low_target.return_value = 7
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        self.assertEqual("User stories zijn maximaal 5 dagen gemiddeld in progress. "
                         "Meer dan 7 dagen gemiddeld in progress is rood.", duration_metric.norm())

    def test_extra_info_no_metric_source(self):
        """ Test that the None is returned as extra info if there is no metric source. """
        self.__project.metric_sources.return_value = []
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        self.assertEqual(None, duration_metric.extra_info())

    def test_value_empty_metric_source(self):
        """ Test that the value method returns -1 if the metric source is None. """
        self.__project.metric_sources.return_value = [None]
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        self.assertEqual(-1, duration_metric.value())


class UserStoriesInProgressTest(unittest.TestCase):
    """ Unit tests for the number of user stories in progress metric. """

    def setUp(self):
        self.__project = unittest.mock.create_autospec(domain.Project, instance=True)
        self.__subject = MagicMock()

    def test_norm(self):
        """ Test that the norm is correct. """
        self.__subject.target.return_value = 5
        self.__subject.low_target.return_value = 7
        progress_metric = metric.UserStoriesInProgress(project=self.__project, subject=self.__subject)

        self.assertEqual("Maximaal 5 stories in progress. Meer dan 7 stories in progress is rood.",
                         progress_metric.norm())

    def test_value(self):
        """ Test that the value is correct. """
        mock_metric_source = MagicMock()
        mock_metric_source.nr_issues.return_value = (12, [])
        self.__project.metric_sources = MagicMock(return_value=[mock_metric_source])
        progress_metric = metric.UserStoriesInProgress(project=self.__project, subject=self.__subject)

        self.assertEqual(12, progress_metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        mock_metric_source = MagicMock()
        mock_metric_source.nr_issues.return_value = (12, [])
        self.__project.metric_sources = MagicMock(return_value=[mock_metric_source])
        self.__subject.name.return_value = "Foo"
        progress_metric = metric.UserStoriesInProgress(project=self.__project, subject=self.__subject)

        self.assertEqual("Foo heeft 12 stories in progress.", progress_metric.report())

    def test_status(self):
        """ Test that the status is correct. """
        mock_metric_source = MagicMock()
        mock_metric_source.nr_issues.return_value = (3, [])
        self.__project.metric_sources = MagicMock(return_value=[mock_metric_source])
        self.__subject.target.return_value = None
        self.__subject.low_target.return_value = None
        progress_metric = metric.UserStoriesInProgress(project=self.__project, subject=self.__subject)

        self.assertEqual("green", progress_metric.status())

    def test_value_empty_metric_source(self):
        """ Test that the value method returns -1 if the metric source is None. """
        self.__project.metric_sources = MagicMock(return_value=[None])
        progress_metric = metric.UserStoriesInProgress(project=self.__project, subject=self.__subject)

        self.assertEqual(-1, progress_metric.value())


class UserStoriesWithoutSecurityRiskTest(unittest.TestCase):
    """ Unit tests for the number of user stories without security risk assessment metric. """

    def setUp(self):
        jira = FakeJiraFilter()
        self.__project = domain.Project(
            metric_sources={metric_source.UserStoryWithoutSecurityRiskAssessmentTracker: jira},
            metric_source_ids={jira: '12345'})
        self.__metric = metric.UserStoriesWithoutSecurityRiskAssessment(project=self.__project, subject=self.__project)

    def test_norm(self):
        """ Test that the norm is correct. """
        self.assertEqual("Maximaal 1 ready user stories zonder security risk beoordeling. "
                         "Meer dan 3 ready user stories zonder security risk beoordeling is rood.",
                         self.__metric.norm())

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(12, self.__metric.value())

    def test_report(self):
        """ Test that the report of the metric is correct. """
        self.assertEqual("Het aantal ready user stories zonder security risk beoordeling is 12.",
                         self.__metric.report())


class UserStoriesWithoutPerformanceRiskTest(unittest.TestCase):
    """ Unit tests for the number of user stories without performance risk assessment metric. """

    def setUp(self):
        jira = FakeJiraFilter()
        self.__project = domain.Project(
            metric_sources={metric_source.UserStoryWithoutPerformanceRiskAssessmentTracker: jira},
            metric_source_ids={jira: '12345'})
        self.__metric = metric.UserStoriesWithoutPerformanceRiskAssessment(project=self.__project,
                                                                           subject=self.__project)

    def test_norm(self):
        """ Test that the norm is correct. """
        self.assertEqual("Maximaal 1 ready user stories zonder performance risk beoordeling. "
                         "Meer dan 3 ready user stories zonder performance risk beoordeling is rood.",
                         self.__metric.norm())

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(12, self.__metric.value())


class PredictedNumberOfFinishedUserStoryPointsTest(unittest.TestCase):
    """ Unit tests for the predicted number of finished user story points metric. """

    def test_norm(self):
        """ Test that the norm is correct. """
        prediction = metric.PredictedNumberOfFinishedUserStoryPoints(project=domain.Project())
        self.assertEqual("Het voorspelde aantal user story punten voor de huidige sprint is tenminste 90% van het "
                         "geplande aantal user story punten. De metriek is rood als de voorspelling minder dan 80% "
                         "van het geplande aantal user story punten is.", prediction.norm())

    def test_value(self):
        """ Test that the value is correct. """
        predictor = unittest.mock.Mock()
        predictor.predicted_number_of_user_story_points.return_value = 20
        predictor.planned_number_of_user_story_points.return_value = 20
        project = domain.Project(metric_sources={metric_source.UserStoryPointsPredictor: predictor},
                                 metric_source_ids={predictor: "project"})
        prediction = metric.PredictedNumberOfFinishedUserStoryPoints(project=project, subject=project)
        self.assertEqual(100., prediction.value())

    def test_value_without_metric_source(self):
        """ Test that the value is -1 if the metric has no metric source. """
        self.assertEqual(-1, metric.PredictedNumberOfFinishedUserStoryPoints(project=domain.Project()).value())

    def test_value_when_planned_user_story_points_is_zero(self):
        """ Test that the value is -1 if the planned number of user story points is zero. """
        predictor = unittest.mock.Mock()
        predictor.predicted_number_of_user_story_points.return_value = 20
        predictor.planned_number_of_user_story_points.return_value = 0
        project = domain.Project(metric_sources={metric_source.UserStoryPointsPredictor: predictor},
                                 metric_source_ids={predictor: "project"})
        prediction = metric.PredictedNumberOfFinishedUserStoryPoints(project=project, subject=project)
        self.assertEqual(-1, prediction.value())

    def test_value_without_metric_source_id(self):
        """ Test that the value is -1 if the metric has no metric source id. """
        predictor = unittest.mock.Mock()
        project = domain.Project(metric_sources={metric_source.UserStoryPointsPredictor: predictor})
        self.assertEqual(-1, metric.PredictedNumberOfFinishedUserStoryPoints(project=project, subject=project).value())

    def test_report(self):
        """ Test that the report is correct. """
        predictor = unittest.mock.Mock()
        predictor.predicted_number_of_user_story_points.return_value = 20
        predictor.planned_number_of_user_story_points.return_value = 20
        project = domain.Project(metric_sources={metric_source.UserStoryPointsPredictor: predictor},
                                 metric_source_ids={predictor: "project"})
        prediction = metric.PredictedNumberOfFinishedUserStoryPoints(project=project, subject=project)
        self.assertEqual("Het voorspelde aantal user story punten (20) voor de huidige sprint is 100% van het "
                         "geplande aantal user story punten (20).", prediction.report())

    def test_report_decimals(self):
        """ Test that the report rounds the percentage. """
        predictor = unittest.mock.Mock()
        predictor.predicted_number_of_user_story_points.return_value = 20
        predictor.planned_number_of_user_story_points.return_value = 21
        project = domain.Project(metric_sources={metric_source.UserStoryPointsPredictor: predictor},
                                 metric_source_ids={predictor: "project"})
        prediction = metric.PredictedNumberOfFinishedUserStoryPoints(project=project, subject=project)
        self.assertEqual("Het voorspelde aantal user story punten (20) voor de huidige sprint is 95% van het "
                         "geplande aantal user story punten (21).", prediction.report())

    def test_report_without_metric_source(self):
        """ Test that the report is correct when there is no metric source. """
        project = domain.Project()
        prediction = metric.PredictedNumberOfFinishedUserStoryPoints(project=project, subject=project)
        self.assertEqual("De voorspelling van het percentage user story punten dat in de huidige sprint zal worden "
                         "opgeleverd van <no name> kon niet gemeten worden omdat de bron UserStoryPointsPredictor niet "
                         "is geconfigureerd.", prediction.report())
