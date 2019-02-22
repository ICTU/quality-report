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

import time
import ssl
import logging
import datetime
import xml.etree.cElementTree
import urllib.error
from typing import List
import unittest
from unittest.mock import patch, call, MagicMock

from hqlib.metric_source import Checkmarx, url_opener


PROJECTS = '[{"id": 11, "name": "metric_source_id"}, {"id": 22, "name": "id2"}]'
LAST_SCAN = '[{"id": 10111, "dateAndTime": {"finishedOn": "2017-10-24T20:00:47.553"}}]'
STATISTICS = '{"highSeverity": 4, "mediumSeverity": 7}'

SAST_REPORT = '''<?xml version="1.0" encoding="utf-8"?>
<CxXMLResults>
  <Query id="789" name="Reflected_XSS" group="JScript_Vulnerabilities" Severity="{severity}" QueryVersionCode="842956">
    <Result Status="Recurrent" FalsePositive="{false_positive}" >
    </Result>
  </Query>
</CxXMLResults>
'''


class CheckmarxIssueTest(unittest.TestCase):
    """ Unit tests for Issue class. """

    def test_issue(self):
        """ Test if issue is created correctly. """
        issue = Checkmarx.Issue('a_group', 'the_name', 'http://url', 3, 'New')

        self.assertEqual('a group', issue.group)
        self.assertEqual('the name', issue.title)
        self.assertEqual('http://url', issue.display_url)
        self.assertEqual(3, issue.count)
        self.assertEqual('New', issue.status)


class CheckmarxConstructorTest(unittest.TestCase):
    """ Unit tests for constructor of Checkmarx class. """

    # pylint: disable=too-many-public-methods

    def setUp(self):
        # pylint: disable=protected-access
        Checkmarx._Checkmarx__retrieve_access_token.cache_clear()

    @patch.object(logging, 'error')
    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_checkmarx_init(self, mock_url_read, mock_error):
        """ Test that initialization of checkmarx goes correctly. """
        mock_url_read.return_value = '{"access_token": "abc123"}'
        marx = Checkmarx(url='http://url', username='un', password='pwd')  # nosec

        self.assertIsNotNone(marx)
        mock_url_read.assert_called_once_with(
            'http://url/cxrestapi/auth/identity/connect/token',
            post_body=b'username=un&password=pwd&scope=sast_rest_api&grant_type=password&'
                      b'client_id=resource_owner_client&client_secret=014DF517-39D1-4453-B7B3-9930C563627C')
        mock_error.assert_not_called()

    @patch('ssl._create_unverified_context')
    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_checkmarx_init_no_ssl(self, mock_url_read, mock_create_unverified_context):
        """ Test that initialization of checkmarx goes correctly without ssl. """
        # pylint: disable=protected-access
        delattr(ssl, '_create_unverified_context')
        mock_url_read.return_value = '{"access_token": "abc123"}'
        marx = Checkmarx(url='http://url', username='un', password='pwd')  # nosec

        self.assertIsNotNone(marx)
        self.assertFalse(hasattr(ssl, '_create_unverified_context'))
        self.assertTrue(hasattr(ssl, '_create_default_https_context'))
        mock_create_unverified_context.assert_not_called()

    @patch.object(logging, 'error')
    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_checkmarx_init_http_error(self, mock_url_read, mock_error):
        """ Test initialization of checkmarx when http error occures. """
        mock_url_read.side_effect = urllib.error.HTTPError('raise', None, None, None, None)
        marx = Checkmarx(url='http://url', username='un', password='pwd')  # nosec

        self.assertIsNotNone(marx)
        mock_url_read.assert_called_once_with(
            'http://url/cxrestapi/auth/identity/connect/token',
            post_body=b'username=un&password=pwd&scope=sast_rest_api&grant_type=password&'
                      b'client_id=resource_owner_client&client_secret=014DF517-39D1-4453-B7B3-9930C563627C')
        mock_error.assert_called_once_with("HTTP error during the retrieving of access token!")

    @patch.object(logging, 'error')
    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_checkmarx_init_invalid_jon_error(self, mock_url_read, mock_error):
        """ Test initialization of checkmarx with invalid json response. """
        mock_url_read.return_value = 'non-json'
        marx = Checkmarx(url='http://url', username='un', password='pwd')  # nosec

        self.assertIsNotNone(marx)
        mock_url_read.assert_called_once_with(
            'http://url/cxrestapi/auth/identity/connect/token',
            post_body=b'username=un&password=pwd&scope=sast_rest_api&grant_type=password&'
                      b'client_id=resource_owner_client&client_secret=014DF517-39D1-4453-B7B3-9930C563627C')
        self.assertEqual(mock_error.call_args[0][0], "Couldn't load access token from json: %s.")
        self.assertIsInstance(mock_error.call_args[0][1], ValueError)

    @patch.object(logging, 'error')
    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_checkmarx_init_key_missing_error(self, mock_url_read, mock_error):
        """ Test initialization of checkmarx with invalid json response. """
        # pylint: disable=protected-access
        mock_url_read.return_value = '{}'
        marx = Checkmarx(url='http://url', username='un', password='pwd')  # nosec

        self.assertIsNotNone(marx)
        mock_url_read.assert_called_once_with(
            'http://url/cxrestapi/auth/identity/connect/token',
            post_body=b'username=un&password=pwd&scope=sast_rest_api&grant_type=password&'
                      b'client_id=resource_owner_client&client_secret=014DF517-39D1-4453-B7B3-9930C563627C')
        self.assertEqual(mock_error.call_args[0][0], "Couldn't load access token from json: %s.")
        self.assertIsInstance(mock_error.call_args[0][1], KeyError)
        self.assertEqual(ssl._create_default_https_context, ssl._create_unverified_context)


@patch.object(url_opener.UrlOpener, 'url_read')
class CheckmarxTest(unittest.TestCase):
    """ Unit tests for the Checkmarx class. """

    # pylint: disable=too-many-public-methods

    def setUp(self):
        time.sleep = MagicMock()
        # pylint: disable=protected-access
        Checkmarx._fetch_project_id.cache_clear()
        with patch.object(url_opener.UrlOpener, 'url_read', return_value='{"access_token": "abc123"}'):
            self.__report = Checkmarx('http://url', 'username', 'password')

    def test_high_risk_warnings(self, mock_url_read):
        """ Test the number of high risk warnings. """
        mock_url_read.side_effect = [PROJECTS, LAST_SCAN, STATISTICS]
        self.assertEqual(4, self.__report.nr_warnings(['metric_source_id'], 'high'))

        self.assertEqual(mock_url_read.call_args_list[0][0][0], 'http://url/CxRestAPI/projects')
        self.assertEqual(mock_url_read.call_args_list[1][0][0], 'http://url/CxRestAPI/sast/scans?projectId=11&last=1')
        self.assertEqual(mock_url_read.call_args_list[2][0][0],
                         'http://url/CxRestAPI/sast/scans/10111/resultsStatistics')

    @patch.object(logging, 'error')
    def test_nr_warnings_no_project(self, mock_error, mock_url_read):
        """ Test the number of high risk warnings. """
        mock_url_read.return_value = PROJECTS
        self.assertEqual(-1, self.__report.nr_warnings(['unknown_proj_id'], 'high'))
        mock_error.assert_called_once_with("Error: no project id found for project with name '%s'.", 'unknown_proj_id')

    def test_obtain_issues(self, mock_url_read):
        """ Test that issues are correctly obtained. """
        mock_url_read.side_effect = [PROJECTS, LAST_SCAN, '{"reportId": 22}', '{"status": {"value": "Created"}}',
                                     SAST_REPORT.format(false_positive=False, severity='High')]

        self.__report.obtain_issues(['metric_source_id'], 'high')
        issues = self.__report.issues()

        self.assertIsInstance(issues, List)
        self.assertIsInstance(issues[0], Checkmarx.Issue)
        self.assertEqual('JScript Vulnerabilities', issues[0].group)
        self.assertEqual('Reflected XSS', issues[0].title)
        self.assertEqual('http://url/CxWebClient/ScanQueryDescription.aspx?queryID=789&'
                         'queryVersionCode=842956&queryTitle=Reflected_XSS', issues[0].display_url)
        self.assertEqual(1, issues[0].count)
        self.assertEqual("Recurrent", issues[0].status)
        self.assertEqual(mock_url_read.call_args_list[0][0][0], 'http://url/CxRestAPI/projects')
        self.assertEqual(mock_url_read.call_args_list[1][0][0], 'http://url/CxRestAPI/sast/scans?projectId=11&last=1')
        self.assertEqual(mock_url_read.call_args_list[2][0][0], 'http://url/CxRestAPI/reports/sastScan')
        self.assertEqual(mock_url_read.call_args_list[3][0][0], 'http://url/CxRestAPI/reports/sastScan/22/status')
        self.assertEqual(mock_url_read.call_args_list[4][0][0], 'http://url/CxRestAPI/reports/sastScan/22')

    @patch.object(logging, 'error')
    def test_obtain_issues_xml_error(self, mock_error, mock_url_read):
        """ Test that issues are correctly obtained. """
        mock_url_read.side_effect = \
            [PROJECTS, LAST_SCAN, '{"reportId": 22}', '{"status": {"value": "Created"}}', 'not-an-xml']
        self.__report.obtain_issues(['metric_source_id'], 'high')

        issues = self.__report.issues()

        self.assertIsInstance(issues, List)
        self.assertEqual(len(issues), 0)
        self.assertEqual(mock_error.call_args[0][0], "Error in checkmarx report xml: %s.")
        self.assertIsInstance(mock_error.call_args[0][1], xml.etree.ElementTree.ParseError)

    @patch.object(logging, 'error')
    def test_obtain_issue_ssast_report_not_created(self, mock_error, mock_url_read):
        """ Test that issues are correctly obtained. """
        mock_url_read.side_effect = [PROJECTS, LAST_SCAN, '{"reportId": 22}'] + \
                                    ['{"status": {"value": "InProgress"}}'] * 10
        self.__report.obtain_issues(['metric_source_id'], 'high')

        issues = self.__report.issues()

        self.assertIsInstance(issues, List)
        self.assertEqual(len(issues), 0)
        mock_error.assert_called_once_with("SAST report is not created on the Checkmarx server!")

    @patch.object(logging, 'error')
    def test_obtain_issues_xml_tag_error(self, mock_error, mock_url_read):
        """ Test that issues are correctly obtained. """
        mock_url_read.side_effect = [PROJECTS, LAST_SCAN, '{"reportId": 22}', '{"status": {"value": "Created"}}',
                                     '<CxXMLResults><Query /></CxXMLResults>']
        self.__report.obtain_issues(['metric_source_id'], 'high')

        issues = self.__report.issues()

        self.assertIsInstance(issues, List)
        self.assertEqual(len(issues), 0)
        self.assertEqual(mock_error.call_args[0][0], "Tag %s could not be found.")
        self.assertIsInstance(mock_error.call_args[0][1], KeyError)

    def test_obtain_issues_exclude_false_positives(self, mock_url_read):
        """ Test that issues are omitted when false positive. """
        mock_url_read.side_effect = [PROJECTS, LAST_SCAN, '{"reportId": 22}', '{"status": {"value": "Created"}}',
                                     SAST_REPORT.format(false_positive=True, severity='High')]
        self.__report.obtain_issues(['metric_source_id'], 'high')
        issues = self.__report.issues()
        self.assertIsInstance(issues, List)
        self.assertEqual(len(issues), 0)

    def test_obtain_issues_exclude_wrong_severity(self, mock_url_read):
        """ Test that issues are omitted when severity does not match. """
        mock_url_read.side_effect = [PROJECTS, LAST_SCAN, '{"reportId": 22}', '{"status": {"value": "Created"}}',
                                     SAST_REPORT.format(false_positive=False, severity='Low')]
        self.__report.obtain_issues(['metric_source_id'], 'high')
        issues = self.__report.issues()
        self.assertIsInstance(issues, List)
        self.assertEqual(len(issues), 0)

    def test_obtain_issues_no_query(self, mock_url_read):
        """ Test that issues are omitted when there is no query. """
        mock_url_read.side_effect = \
            [PROJECTS, LAST_SCAN, '{"reportId": 22}', '{"status": {"value": "Created"}}', '<CxXMLResults />']
        self.__report.obtain_issues(['metric_source_id'], 'high')
        issues = self.__report.issues()
        self.assertIsInstance(issues, List)
        self.assertEqual(len(issues), 0)

    def test_obtain_issues_http_error(self, mock_url_read):
        """ Test that issues are omitted when http error occurs. """
        mock_url_read.side_effect = urllib.error.HTTPError('raise', None, None, None, None)
        self.__report.obtain_issues(['metric_source_id'], 'high')
        issues = self.__report.issues()
        self.assertIsInstance(issues, List)
        self.assertEqual(len(issues), 0)

    @patch.object(logging, 'error')
    def test_obtain_issues_response_error(self, mock_error, mock_url_read):
        """ Test that issues are omitted when json error occurs. """
        mock_url_read.return_value = 'non-json'
        self.__report.obtain_issues(['metric_source_id'], 'high')
        issues = self.__report.issues()
        self.assertIsInstance(issues, List)
        self.assertEqual(len(issues), 0)
        self.assertEqual(mock_error.call_args[0][0], "Error loading json: %s.")
        self.assertIsInstance(mock_error.call_args[0][1], ValueError)

    @patch.object(logging, 'error')
    def test_obtain_issues_json_error(self, mock_error, mock_url_read):
        """ Test that issues are omitted when json error occurs. """
        mock_url_read.side_effect = [PROJECTS, '{}']
        self.__report.obtain_issues(['metric_source_id'], 'high')
        issues = self.__report.issues()
        self.assertIsInstance(issues, List)
        self.assertEqual(len(issues), 0)
        self.assertEqual(mock_error.call_args[0][0], "Tag %s could not be found.")
        self.assertIsInstance(mock_error.call_args[0][1], KeyError)

    def test_medium_risk_warnings(self, mock_url_read):
        """ Test the number of medium risk warnings. """
        mock_url_read.side_effect = [PROJECTS, LAST_SCAN, STATISTICS]
        self.assertEqual(7, self.__report.nr_warnings(['metric_source_id'], 'medium'))

    def test_passed_raise(self, mock_url_read):
        """ Test that the value is -1 when the report can't be opened. """
        mock_url_read.side_effect = urllib.error.HTTPError('raise', None, None, None, None)
        self.assertEqual(-1, self.__report.nr_warnings(['raise'], 'high'))
        mock_url_read.assert_called_once_with('http://url/CxRestAPI/projects')

    def test_multiple_urls(self, mock_url_read):
        """ Test the number of alerts for multiple urls. """
        mock_url_read.side_effect = [PROJECTS, LAST_SCAN, STATISTICS, PROJECTS, '[{"id": 202222}]', STATISTICS]
        self.assertEqual(14, self.__report.nr_warnings(['metric_source_id', 'id2'], 'medium'))
        self.assertEqual([
            call('http://url/CxRestAPI/projects'),
            call('http://url/CxRestAPI/sast/scans?projectId=11&last=1'),
            call('http://url/CxRestAPI/sast/scans/10111/resultsStatistics'),
            call('http://url/CxRestAPI/projects'),
            call('http://url/CxRestAPI/sast/scans?projectId=22&last=1'),
            call('http://url/CxRestAPI/sast/scans/202222/resultsStatistics')
        ], mock_url_read.call_args_list)

    def test_metric_source_urls_without_report(self, mock_url_read):
        """ Test the metric source urls without metric ids. """
        mock_url_read.return_value = None
        self.assertEqual([], self.__report.metric_source_urls())

    def test_metric_source_urls(self, mock_url_read):
        """ Test the metric source urls with one metric id. """
        mock_url_read.side_effect = [PROJECTS, LAST_SCAN]
        self.assertEqual(['http://url/CxWebClient/ViewerMain.aspx?scanId=10111&ProjectID=22'],
                         self.__report.metric_source_urls('id2'))

    @patch.object(logging, 'error')
    def test_metric_source_urls_key_error(self, mock_error, mock_url_read):
        """ Test the metric source urls with empty scan response.. """
        mock_url_read.side_effect = [PROJECTS, '{}']
        self.assertEqual(["http://url/"], self.__report.metric_source_urls('id2'))
        self.assertEqual(mock_error.call_args_list[0][0][0], "Couldn't load values from json: %s - %s")
        self.assertEqual(mock_error.call_args_list[0][0][1], 'id2')
        self.assertIsInstance(mock_error.call_args_list[0][0][2], KeyError)

    @patch.object(logging, 'error')
    def test_metric_source_urls_index_error(self, mock_error, mock_url_read):
        """ Test the metric source urls with empty scan response.. """
        mock_url_read.side_effect = [PROJECTS, '[]']
        self.assertEqual(["http://url/"], self.__report.metric_source_urls('id2'))

        self.assertEqual(mock_error.call_args_list[0][0][0], "Couldn't load values from json: %s - %s")
        self.assertEqual(mock_error.call_args_list[0][0][1], 'id2')
        self.assertIsInstance(mock_error.call_args_list[0][0][2], IndexError)

    def test_metric_source_urls_on_error(self, mock_url_read):
        """ Test the metric source urls when an error occurs. """
        mock_url_read.side_effect = [PROJECTS, urllib.error.HTTPError(None, None, None, None, None)]
        self.assertEqual(["http://url/"], self.__report.metric_source_urls('id2'))
        self.assertEqual([
            call('http://url/CxRestAPI/projects'),
            call('http://url/CxRestAPI/sast/scans?projectId=22&last=1')
        ], mock_url_read.call_args_list)

    def test_url(self, mock_url_read):
        """ Test the metric source base url. """
        mock_url_read.return_value = LAST_SCAN
        self.assertEqual("http://url/", self.__report.url())

    def test_datetime(self, mock_url_read):
        """ Test the date and time of the report. """
        mock_url_read.side_effect = [PROJECTS, LAST_SCAN]
        self.assertEqual(datetime.datetime(2017, 10, 24, 20, 0, 47), self.__report.datetime('id2'))
        self.assertEqual([
            call('http://url/CxRestAPI/projects'),
            call('http://url/CxRestAPI/sast/scans?projectId=22&last=1')
        ], mock_url_read.call_args_list)

    def test_datetime_http_error(self, mock_url_read):
        """ Test the date and time of the report. """
        mock_url_read.side_effect = [PROJECTS, urllib.error.HTTPError(None, None, None, None, None)]
        self.assertEqual(datetime.datetime.min, self.__report.datetime('id2'))
        self.assertEqual([
            call('http://url/CxRestAPI/projects'),
            call('http://url/CxRestAPI/sast/scans?projectId=22&last=1')
        ], mock_url_read.call_args_list)

    @patch.object(logging, 'error')
    def test_datetime_missing(self, mock_error, mock_url_read):
        """ Test a missing date and time of the report. """
        mock_url_read.side_effect = [PROJECTS, '[{"id": 202222}]']
        self.assertEqual(datetime.datetime.min, self.__report.datetime('id2'))
        self.assertEqual(mock_error.call_args_list[0][0][0], "Couldn't parse date and time for project %s from %s: %s")
        self.assertEqual(mock_error.call_args_list[0][0][1], 'id2')
        self.assertEqual(mock_error.call_args_list[0][0][2], 'http://url/')
        self.assertIsInstance(mock_error.call_args_list[0][0][3], KeyError)

    @patch.object(logging, 'error')
    def test_datetime_empty_scan(self, mock_error, mock_url_read):
        """ Test a missing scan data. """
        mock_url_read.side_effect = [PROJECTS, '[]']
        self.assertEqual(datetime.datetime.min, self.__report.datetime('id2'))
        self.assertEqual(mock_error.call_args_list[0][0][0], "Couldn't parse date and time for project %s from %s: %s")
        self.assertEqual(mock_error.call_args_list[0][0][1], 'id2')
        self.assertEqual(mock_error.call_args_list[0][0][2], 'http://url/')
        self.assertIsInstance(mock_error.call_args_list[0][0][3], IndexError)

    @patch.object(logging, 'error')
    def test_datetime_format_error(self, mock_error, mock_url_read):
        """ Test a invalid date and time of the report. """
        mock_url_read.side_effect = [PROJECTS, '[{"id": 3, "dateAndTime": {"finishedOn": "2017-40-24T20:00:47.553"}}]']
        self.assertEqual(datetime.datetime.min, self.__report.datetime('id2'))
        self.assertEqual(mock_error.call_args_list[0][0][0], "Couldn't parse date and time for project %s from %s: %s")
        self.assertEqual(mock_error.call_args_list[0][0][1], 'id2')
        self.assertEqual(mock_error.call_args_list[0][0][2], 'http://url/')
        self.assertIsInstance(mock_error.call_args_list[0][0][3], ValueError)

    @patch.object(logging, 'error')
    def test_nr_warnings_on_missing_values(self, mock_error, mock_url_read):
        """ Test dealing with empty list of values. """
        mock_url_read.side_effect = [PROJECTS, '{}']
        self.assertEqual(-1, self.__report.nr_warnings(['id2'], 'medium'))
        self.assertEqual(mock_error.call_args_list[0][0][0],
                         "Couldn't parse alerts for project %s with %s risk level from %s: %s")
        self.assertEqual(mock_error.call_args_list[0][0][1], 'id2')
        self.assertEqual(mock_error.call_args_list[0][0][2], 'medium')
        self.assertEqual(mock_error.call_args_list[0][0][3], 'http://url/')
        self.assertIsInstance(mock_error.call_args_list[0][0][4], KeyError)
