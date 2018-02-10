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
import unittest
import urllib.error
from json import JSONDecodeError
from unittest.mock import patch, call

from hqlib.metric_source import Jira, url_opener


@patch.object(url_opener.UrlOpener, '__init__')
class JiraConstructorTests(unittest.TestCase):
    """ Unit tests of the constructor of the Jira class. """

    def test_url_opener_constructor(self, init_mock):
        """" Test that by Jira initialisation, UrlOpener is initialised with user name and password as parameters. """
        init_mock.return_value = None

        Jira('http://jira/', 'jira_username', 'jira_password')

        init_mock.assert_called_with(username='jira_username', password='jira_password')

    def test_url_is_padded(self, init_mock):
        """" Tests that jira url is padded if needed."""
        init_mock.return_value = None

        jira = Jira('X', '', '')

        self.assertEqual('X/', jira._Jira__url)

    def test_url_padding(self, init_mock):
        """" Tests that jira url is not padded if not needed."""
        init_mock.return_value = None

        jira = Jira('X/', '', '')

        self.assertEqual('X/', jira._Jira__url)


@patch.object(url_opener.UrlOpener, 'url_read')
class JiraTest(unittest.TestCase):
    """ Unit tests for the Jira class. """

    def test_query_total(self, url_read_mock):
        """ Test that the correct number of issues is returned. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.side_effect = ['{"searchUrl":"http://jira/search?filter_criteria"}',
                                     '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}']

        result = jira.query_total(12345)

        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/12345'),
            call('http://jira/search?filter_criteria')])
        self.assertEqual(5, result)

    def test_query_total_zero(self, url_read_mock):
        """ Test that the correct number of issues is returned when there are no issues in the filter. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.side_effect = ['{"searchUrl":"http://jira/search?filter_criteria"}',
                                     '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "0"}']

        result = jira.query_total(12345)

        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/12345'),
            call('http://jira/search?filter_criteria')])
        self.assertEqual(0, result)

    def test_query_total_without_query(self, url_read_mock):
        """ Test that the result is -1 when no query id is passed. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.return_value = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'

        result = jira.query_total('')

        url_read_mock.assert_not_called()
        self.assertEqual(-1, result)

    def test_query_total_on_http_error(self, url_read_mock):
        """ Test that the result is -1 when an HTTP error occurs. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.side_effect = urllib.error.HTTPError(None, None, None, None, None)

        result = jira.query_total(12345)

        url_read_mock.has_call(call('http://jira/rest/api/2/filter/12345'))
        self.assertEqual(-1, result)

    def test_query_total_on_http_error_during_second_call(self, url_read_mock):
        """ Test that the result is -1 when an HTTP error occurs during the second call to Jira. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.side_effect = ['{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view"}',
                                     urllib.error.HTTPError(None, None, None, None, None)]

        result = jira.query_total(12345)

        url_read_mock.has_calls([call('http://jira/rest/api/2/filter/12345'), call('http://jira/search?')])
        self.assertEqual(-1, result)

    def test_get_duration_of_stories(self, url_read_mock):
        """ Test that the average number of days a story spent in status 'In Progress' is correct. """
        issue = "ISSUE-1"
        issue2 = "ISSUE-2"
        jira = Jira('http://jira/', 'username', 'password')
        search_json = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'
        issues_json = '{"total": "5", "issues": [{"key": "' + \
                      issue + '", "fields": {"summary": "Issue Title"}}, {"key": "' + \
                      issue2 + '", "fields": {"summary": "Issue2 Title"}}]}'
        changelog_json = '{"id": "133274", "changelog": { "histories": [' \
                         '{"created": "2017-12-15T23:54:15.000+0100", "items": [' \
                         '{"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]}, ' \
                         '{"created": "2017-11-15T23:54:15.000+0100", "items": [' \
                         '{"field": "Flagged", "fieldtype": "custom", "fromString": "X", "toString": "X"}]}, ' \
                         '{"created": "2017-12-25T09:59:15.000+0100", "items": [' \
                         '{"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}]}}'
        changelog_json2 = '{"id": "133274", "changelog": { "histories": [' \
                          '{"created": "2017-11-15T08:54:15.000+0100", "items": [' \
                          '{"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]}, ' \
                          '{"created": "2017-11-16T09:59:15.000+0100", "items": [' \
                          '{"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}]}}'
        url_read_mock.side_effect = [search_json, issues_json, changelog_json, changelog_json2]

        result = jira.average_duration_of_issues(12345)

        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/12345'),
            call('http://jira/search?'),
            call('http://jira/rest/api/2/issue/{issue}?expand=changelog&fields="*all,-comment"'.format(issue=issue)),
            call('http://jira/rest/api/2/issue/{issue}?expand=changelog&fields="*all,-comment"'.format(issue=issue2))])
        self.assertEqual(5, result)

    def test_extra_info_duration_of_stories_ok(self, url_read_mock):
        """ Test that the content of extra info for a story is correct. """
        issue = "ISSUE-1"
        jira = Jira('http://jira/', 'username', 'password')
        search_json = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'
        issues_json = '{"total": "5", "issues": [{"key": "' + issue + '", "fields": {"summary": "Issue Title"}}]}'
        changelog_json = '{"id": "133274", "changelog": { "histories": [' \
                         '{"created": "2017-12-15T23:54:15.000+0100", "items": [' \
                         '{"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]}, ' \
                         '{"created": "2017-11-15T23:54:15.000+0100", "items": [' \
                         '{"field": "Flagged", "fieldtype": "custom", "fromString": "X", "toString": "X"}]}, ' \
                         '{"created": "2017-12-25T09:59:15.000+0100", "items": [' \
                         '{"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}]}}'
        url_read_mock.side_effect = [search_json, issues_json, changelog_json]

        jira.average_duration_of_issues(12345)
        result = jira.extra_info()

        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/12345'),
            call('http://jira/search?'),
            call('http://jira/rest/api/2/issue/{issue}?expand=changelog&fields="*all,-comment"'.format(issue=issue))])
        self.assertEqual('15 december 2017', result[0].data[0]['day_in'])
        self.assertEqual('25 december 2017', result[0].data[0]['day_out'])
        self.assertEqual(False, result[0].data[0]['is_omitted'])
        self.assertEqual(9, result[0].data[0]['days'])

    def test_extra_info_stories_still_in_progress(self, url_read_mock):
        """ Test that the content of extra info for a story still in progress is correct. """
        issue = "ISSUE-1"
        jira = Jira('http://jira/', 'username', 'password')
        search_json = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'
        issues_json = '{"total": "5", "issues": [{"key": "' + issue + '", "fields": {"summary": "Issue Title"}}]}'
        changelog_json = '{"id": "133274", "changelog": { "histories": [' \
                         '{"created": "2017-12-15T23:54:15.000+0100", "items": [' \
                         '{"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]}]}}'
        url_read_mock.side_effect = [search_json, issues_json, changelog_json]

        jira.average_duration_of_issues(12345)
        result = jira.extra_info()

        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/12345'),
            call('http://jira/search?'),
            call('http://jira/rest/api/2/issue/{issue}?expand=changelog&fields="*all,-comment"'.format(issue=issue))])
        self.assertEqual('15 december 2017', result[0].data[0]['day_in'])
        self.assertEqual('geen', result[0].data[0]['day_out'])
        self.assertEqual(True, result[0].data[0]['is_omitted'])
        self.assertEqual('n.v.t', result[0].data[0]['days'])

    def test_extra_info_stories_never_in_progress(self, url_read_mock):
        """ Test that the content of extra info for a story that never got in progress contains no dates. """
        issue = "ISSUE-1"
        jira = Jira('http://jira/', 'username', 'password')
        search_json = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'
        issues_json = '{"total": "5", "issues": [{"key": "' + issue + '", "fields": {"summary": "Issue Title"}}]}'
        changelog_json = '{"id": "133274", "changelog": { "histories": [' \
                         '{"created": "2017-12-15T23:54:15.000+0100", "items": [' \
                         '{"field": "Flagged", "fieldtype": "custom", "fromString": "X", "toString": "X"}]}]}}'
        url_read_mock.side_effect = [search_json, issues_json, changelog_json]

        jira.average_duration_of_issues(12345)
        result = jira.extra_info()

        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/12345'),
            call('http://jira/search?'),
            call('http://jira/rest/api/2/issue/{issue}?expand=changelog&fields="*all,-comment"'.format(issue=issue))])
        self.assertEqual('geen', result[0].data[0]['day_in'])
        self.assertEqual('geen', result[0].data[0]['day_out'])
        self.assertEqual(True, result[0].data[0]['is_omitted'])
        self.assertEqual('n.v.t', result[0].data[0]['days'])

    def test_extra_info_duration_of_stories_more_than_one(self, url_read_mock):
        """ Test that the content of extra info for multiple stories is correct. """
        issue = "ISSUE-1"
        issue2 = "ISSUE-2"
        jira = Jira('http://jira/', 'username', 'password')
        search_json = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'
        issues_json = '{"total": "5", "issues": [{"key": "' + \
                      issue + '", "fields": {"summary": "Issue Title"}}, {"key": "' + \
                      issue2 + '", "fields": {"summary": "Issue2 Title"}}]}'
        changelog_json = '{"id": "133274", "changelog": { "histories": [' \
                         '{"created": "2017-12-15T23:54:15.000+0100", "items": [' \
                         '{"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]}, ' \
                         '{"created": "2017-11-15T23:54:15.000+0100", "items": [' \
                         '{"field": "Flagged", "fieldtype": "custom", "fromString": "X", "toString": "X"}]}, ' \
                         '{"created": "2017-12-25T09:59:15.000+0100", "items": [' \
                         '{"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}]}}'
        changelog_json2 = '{"id": "133274", "changelog": { "histories": [' \
                          '{"created": "2017-11-15T08:54:15.000+0100", "items": [' \
                          '{"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]}, ' \
                          '{"created": "2017-11-16T09:59:15.000+0100", "items": [' \
                          '{"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}]}}'
        url_read_mock.side_effect = [search_json, issues_json, changelog_json, changelog_json2]

        jira.average_duration_of_issues(12345)
        result = jira.extra_info()

        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/12345'),
            call('http://jira/search?'),
            call('http://jira/rest/api/2/issue/{issue}?expand=changelog&fields="*all,-comment"'.format(issue=issue)),
            call('http://jira/rest/api/2/issue/{issue}?expand=changelog&fields="*all,-comment"'.format(issue=issue2))])
        self.assertEqual('15 december 2017', result[0].data[0]['day_in'])
        self.assertEqual('25 december 2017', result[0].data[0]['day_out'])
        self.assertEqual(9, result[0].data[0]['days'])
        self.assertEqual('15 november 2017', result[0].data[1]['day_in'])
        self.assertEqual('16 november 2017', result[0].data[1]['day_out'])
        self.assertEqual(1, result[0].data[1]['days'])

    def test_get_duration_of_stories_multiple_state_changes(self, url_read_mock):
        """ Test that the number of days from the first enter in status 'In Progress' till the last exit of it
        is correct for multiple status changes. """
        issue = "ISSUE-1"
        jira = Jira('http://jira/', 'username', 'password')
        search_json = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'
        issues_json = '{"total": "5", "issues": [{"key": "' + issue + '", "fields": {"summary": "Issue Title"}}]}'
        changelog_json = '{"id": "133274", "changelog": { "histories": [' \
                         '{"created": "2017-12-15T23:54:15.000+0100", "items": [' \
                         '{"field": "status", "fieldtype": "jira", "fromString": "Op", "toString": "In Progress"}]}, ' \
                         '{"created": "2017-12-16T10:54:15.000+0100", "items": [' \
                         '{"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}, ' \
                         '{"created": "2017-12-16T23:52:15.000+0100", "items": [' \
                         '{"field": "status", "fieldtype": "jira", "fromString": "RO", "toString": "In Progress"}]}, ' \
                         '{"created": "2017-12-25T09:59:15.000+0100", "items": [' \
                         '{"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}]}}'
        url_read_mock.side_effect = [search_json, issues_json, changelog_json]

        result = jira.average_duration_of_issues(12345)

        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/12345'),
            call('http://jira/search?'),
            call('http://jira/rest/api/2/issue/{issue}?expand=changelog&fields="*all,-comment"'.format(issue=issue))])
        self.assertEqual(9, result)

    @patch.object(logging, 'info')
    def test_get_duration_never_got_in_progress_single(self, logging_info_mock, url_read_mock):
        """ Test that the number of days returned is -1 if a single story never entered the state "In Progress". """
        issue = "ISSUE-1"
        jira = Jira('http://jira/', 'username', 'password')
        search_json = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'
        issues_json = '{"total": "5", "issues": [{"key": "' + issue + '", "fields": {"summary": "Issue Title"}}]}'
        changelog_json = '{"id": "133274", "changelog": { "histories": [' \
                         '{"created": "2017-12-15T23:54:15.000+0100", "items": [' \
                         '{"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "Open"}]}]}}'
        url_read_mock.side_effect = [search_json, issues_json, changelog_json]

        result = jira.average_duration_of_issues(12345)

        logging_info_mock.assert_called_with(
            "Invalid date, or issue %s never moved to status 'In Progress'", issue)
        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/12345'),
            call('http://jira/search?'),
            call('http://jira/rest/api/2/issue/{issue}?expand=changelog&fields="*all,-comment"'.format(issue=issue))])
        self.assertEqual(-1, result)

    @patch.object(logging, 'info')
    def test_get_duration_that_never_got_in_progress(self, logging_info_mock, url_read_mock):
        """ Test that story never entered the state "In Progress" does not influence calculated average. """
        issue = "ISSUE-1"
        issue2 = "ISSUE-2"
        jira = Jira('http://jira/', 'username', 'password')
        search_json = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'
        issues_json = '{"total": "5", "issues": [{"key": "' + \
                      issue + '", "fields": {"summary": "Issue Title"}}, {"key": "' + \
                      issue2 + '", "fields": {"summary": "Issue2 Title"}}]}'
        changelog_json = '{"id": "133274", "changelog": { "histories": [' \
                         '{"created": "2017-12-15T23:54:15.000+0100", "items": [' \
                         '{"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "Open"}]}]}}'
        changelog_json2 = '{"id": "133274", "changelog": { "histories": [' \
                          '{"created": "2017-12-15T23:54:15.000+0100", "items": [' \
                          '{"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]}, ' \
                          '{"created": "2017-12-25T09:59:15.000+0100", "items": [' \
                          '{"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}]}}'
        url_read_mock.side_effect = [search_json, issues_json, changelog_json, changelog_json2]

        result = jira.average_duration_of_issues(12345)

        logging_info_mock.assert_called_with(
            "Invalid date, or issue %s never moved to status 'In Progress'", issue)
        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/12345'),
            call('http://jira/search?'),
            call('http://jira/rest/api/2/issue/{issue}?expand=changelog&fields="*all,-comment"'.format(issue=issue)),
            call('http://jira/rest/api/2/issue/{issue}?expand=changelog&fields="*all,-comment"'.format(issue=issue2))])
        self.assertEqual(9, result)

    @patch.object(logging, 'info')
    def test_get_duration_still_in_progress_single(self, logging_info_mock, url_read_mock):
        """ Test that the number of days returned is -1 if a story is still in state "In Progress". """
        issue = "ISSUE-1"
        jira = Jira('http://jira/', 'username', 'password')
        search_json = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'
        issues_json = '{"total": "5", "issues": [{"key": "' + issue + '", "fields": {"summary": "Issue Title"}}]}'
        changelog_json = '{"id": "133274", "changelog": { "histories": [' \
                         '{"created": "2017-12-15T23:54:15.000+0100", "items": [' \
                         '{"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]}]}}'
        url_read_mock.side_effect = [search_json, issues_json, changelog_json]

        result = jira.average_duration_of_issues(12345)

        logging_info_mock.assert_called_with(
            "Invalid date, or issue %s still in status 'In Progress'", issue)
        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/12345'),
            call('http://jira/search?'),
            call('http://jira/rest/api/2/issue/{issue}?expand=changelog&fields="*all,-comment"'.format(issue=issue))])
        self.assertEqual(-1, result)

    @patch.object(logging, 'info')
    def test_get_duration_of_stories_still_in_progress(self, logging_info_mock, url_read_mock):
        """ Test that a story that is still in state "In Progress" does not influence calculated average. """
        issue = "ISSUE-1"
        issue2 = "ISSUE-2"
        jira = Jira('http://jira/', 'username', 'password')
        search_json = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'
        issues_json = '{"total": "5", "issues": [{"key": "' + \
                      issue + '", "fields": {"summary": "Issue Title"}}, {"key": "' + \
                      issue2 + '", "fields": {"summary": "Issue2 Title"}}]}'
        changelog_json = '{"id": "133274", "changelog": { "histories": [' \
                         '{"created": "2017-12-15T23:54:15.000+0100", "items": [' \
                         '{"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]}]}}'
        changelog_json2 = '{"id": "133274", "changelog": { "histories": [' \
                          '{"created": "2017-12-15T23:54:15.000+0100", "items": [' \
                          '{"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]}, ' \
                          '{"created": "2017-12-25T09:59:15.000+0100", "items": [' \
                          '{"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}]}}'
        url_read_mock.side_effect = [search_json, issues_json, changelog_json, changelog_json2]

        result = jira.average_duration_of_issues(12345)

        logging_info_mock.assert_called_with(
            "Invalid date, or issue %s still in status 'In Progress'", issue)
        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/12345'),
            call('http://jira/search?'),
            call('http://jira/rest/api/2/issue/{issue}?expand=changelog&fields="*all,-comment"'.format(issue=issue)),
            call('http://jira/rest/api/2/issue/{issue}?expand=changelog&fields="*all,-comment"'.format(issue=issue2))])
        self.assertEqual(9, result)

    @patch.object(logging, 'info')
    def test_get_duration_of_stories_invalid_to_date(self, logging_info_mock, url_read_mock):
        """ Test that the number of days returned is -1 for a story that has invalid date of progress start. """
        issue = "ISSUE-1"
        jira = Jira('http://jira/', 'username', 'password')
        search_json = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'
        issues_json = '{"total": "5", "issues": [{"key": "' + issue + '", "fields": {"summary": "Issue Title"}}]}'
        changelog_json = '{"id": "133274", "changelog": { "histories": [' \
                         '{"created": "2017-33-15T23:54:15.000+0100", "items": [' \
                         '{"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]}, ' \
                         '{"created": "2017-11-15T23:54:15.000+0100", "items": [' \
                         '{"field": "Flagged", "fieldtype": "custom", "fromString": "X", "toString": "X"}]}, ' \
                         '{"created": "2017-12-25T09:59:15.000+0100", "items": [' \
                         '{"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}]}}'
        url_read_mock.side_effect = [search_json, issues_json, changelog_json]

        result = jira.average_duration_of_issues(12345)

        logging_info_mock.assert_called_with(
            "Invalid date, or issue %s never moved to status 'In Progress'", issue)
        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/12345'),
            call('http://jira/search?'),
            call('http://jira/rest/api/2/issue/{issue}?expand=changelog&fields="*all,-comment"'.format(issue=issue))])
        self.assertEqual(-1, result)

    @patch.object(logging, 'info')
    def test_get_duration_of_stories_invalid_from_date(self, logging_info_mock, url_read_mock):
        """ Test that the number of days returned is -1 for a a story that has invalid date of progress end. """
        issue = "ISSUE-1"
        jira = Jira('http://jira/', 'username', 'password')
        search_json = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'
        issues_json = '{"total": "5", "issues": [{"key": "' + issue + '", "fields": {"summary": "Issue Title"}}]}'
        changelog_json = '{"id": "133274", "changelog": { "histories": [' \
                         '{"created": "2017-12-15T23:54:15.000+0100", "items": [' \
                         '{"field": "status", "fieldtype": "jira", "fromString": "X", "toString": "In Progress"}]}, ' \
                         '{"created": "2017-22-25T09:59:15.000+0100", "items": [' \
                         '{"field": "status", "fieldtype": "jira", "fromString": "In Progress", "toString": "X"}]}]}}'
        url_read_mock.side_effect = [search_json, issues_json, changelog_json]

        result = jira.average_duration_of_issues(12345)

        logging_info_mock.assert_called_with(
            "Invalid date, or issue %s still in status 'In Progress'", issue)
        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/12345'),
            call('http://jira/search?'),
            call('http://jira/rest/api/2/issue/{issue}?expand=changelog&fields="*all,-comment"'.format(issue=issue))])
        self.assertEqual(-1, result)

    @patch.object(logging, 'error')
    def test_get_duration_of_stories_http_error(self, logging_error_mock, url_read_mock):
        """ Test that the number of days returned is -1 if a http error occurs. """
        issue = "ISSUE-1"
        jira = Jira('http://jira/', 'username', 'password')
        search_json = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'
        issues_json = '{"total": "5", "issues": [{"key": "' + issue + '", "fields": {"summary": "Issue Title"}}]}'
        changelog_json = urllib.error.HTTPError(None, None, None, None, None)
        query_id = '12345'
        url_read_mock.side_effect = [search_json, issues_json, changelog_json]

        result = jira.average_duration_of_issues(query_id)

        logging_error_mock.assert_called_with(
            "Error opening jira filter %s: %s.", query_id, changelog_json)
        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/12345'),
            call('http://jira/search?'),
            call('http://jira/rest/api/2/issue/{issue}?expand=changelog&fields="*all,-comment"'.format(issue=issue))])
        self.assertEqual(-1, result)

    @patch.object(logging, 'error')
    def test_get_duration_of_stories_json_error(self, logging_error_mock, url_read_mock):
        """ Test that the number of days returned is -1 if an invalid json is returned as a result. """
        issue = "ISSUE-1"
        jira = Jira('http://jira/', 'username', 'password')
        search_json = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'
        issues_json = '{"total": "5", "issues": [{"key": "' + issue + '", "fields": {"summary": "Issue Title"}}]}'
        changelog_json = 'not a json'
        url_read_mock.side_effect = [search_json, issues_json, changelog_json]

        result = jira.average_duration_of_issues(12345)

        args, _ = logging_error_mock.call_args
        self.assertEqual("Couldn't load json string '%s': %s", args[0])
        self.assertEqual(changelog_json, args[1])
        self.assertTrue(isinstance(args[2], JSONDecodeError))
        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/12345'),
            call('http://jira/search?'),
            call('http://jira/rest/api/2/issue/{issue}?expand=changelog&fields="*all,-comment"'.format(issue=issue))])
        self.assertEqual(-1, result)

    def test_query_sum(self, url_read_mock):
        """ Test that the total number of minutes spend on manual test cases is correct. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.return_value = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", ' \
                                     '"total": "5", "issues": [{"fields": {"customfield_11700": "20"}}, ' \
                                     '{"fields": {"customfield_11700": 100}}, {"fields": {"customfield_11700": null}}]}'

        result = jira.query_sum(12345, 'customfield_11700')

        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/12345'),
            call('http://jira/search?')])
        self.assertEqual(120, result)

    def test_query_sum_zero(self, url_read_mock):
        """ Test that the total number of minutes spend on manual test cases is correct when there are no test
            cases. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.return_value = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", ' \
                                     '"total": "0", "issues": []}'

        result = jira.query_sum(12345, 'customfield_11700')

        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/12345'),
            call('http://jira/search?')])
        self.assertEqual(0, result)

    def test_query_sum_without_query(self, url_read_mock):
        """ Test that the manual test time is -1 when Jira has no query id. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.return_value = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", ' \
                                     '"total": "5", "issues": []}'

        result = jira.query_sum(0, '')

        url_read_mock.assert_not_called()
        self.assertEqual(-1, result)

    def test_query_field_empty(self, url_read_mock):
        """ Test that the number of issues with empty field is correct. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.return_value = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", ' \
                                     '"total": "5", "issues": [{"fields": {"customfield_11700": "20"}}, ' \
                                     '{"fields": {"customfield_11700": 100}}, {"fields": {"customfield_11700": null}}]}'

        result = jira.query_field_empty('filter id', 'customfield_11700')

        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/filter id'),
            call('http://jira/search?')])
        self.assertEqual(1, result)

    def test_query_field_empty_without_issues(self, url_read_mock):
        """ Test that the number of issues with empty field is correct when there are no issues. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.return_value = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", ' \
                                     '"total": "0", "issues": []}'

        result = jira.query_field_empty('filter id', 'customfield_11700')

        url_read_mock.assert_has_calls([
            call('http://jira/rest/api/2/filter/filter id'),
            call('http://jira/search?')])
        self.assertEqual(0, result)

    def test_nr_manual_tests_not_measured_without_query(self, url_read_mock):
        """ Test that the number of issues is -1 when Jira has no query id. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.return_value = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'

        result = jira.query_field_empty('', '')

        url_read_mock.assert_not_called()
        self.assertEqual(-1, result)

    def test_get_query_url_view(self, url_read_mock):
        """ Test that the url is correct. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.return_value = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'

        result = jira.get_query_url('filter id', search=False)

        url_read_mock.assert_called_once_with('http://jira/rest/api/2/filter/filter id')
        self.assertEqual("http://jira/view", result)

    def test_get_query_url_search(self, url_read_mock):
        """ Test that the url is correct. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.return_value = '{"searchUrl": "http://jira/search", "viewUrl": "http://jira/view", "total": "5"}'

        result = jira.get_query_url('filter id', search=True)

        url_read_mock.assert_called_once_with('http://jira/rest/api/2/filter/filter id')
        self.assertEqual("http://jira/search", result)


@patch.object(url_opener.UrlOpener, 'url_read')
class JiraWhenFailingTest(unittest.TestCase):
    """ Unit tests for a Jira that's unavailable. """

    def test_query_total(self, url_read_mock):
        """ Test that the query total is -1 when Jira is not available. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.side_effect = urllib.error.HTTPError(None, None, None, None, None)

        result = jira.query_total('filter id')

        url_read_mock.assert_called_once_with('http://jira/rest/api/2/filter/filter id')
        self.assertEqual(-1, result)

    def test_query_sum(self, url_read_mock):
        """ Test that the query sum is -1 when Jira is not available. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.side_effect = urllib.error.HTTPError(None, None, None, None, None)

        result = jira.query_sum('filter id', 'field')

        url_read_mock.assert_called_once_with('http://jira/rest/api/2/filter/filter id')
        self.assertEqual(-1, result)

    def testquery_field_empty(self, url_read_mock):
        """ Test that the query_field_empty return -1 when Jira is not available. """
        jira = Jira('http://jira/', 'username', 'password')
        url_read_mock.side_effect = urllib.error.HTTPError(None, None, None, None, None)

        result = jira.query_field_empty('filter id', 'field')

        url_read_mock.assert_called_once_with('http://jira/rest/api/2/filter/filter id')
        self.assertEqual(-1, result)
