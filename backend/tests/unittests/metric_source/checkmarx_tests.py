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

import time
import ssl
import logging
import datetime
import xml.etree.cElementTree
import urllib.error
from typing import List
import unittest
from unittest.mock import patch, call

from hqlib.metric_source import Checkmarx, url_opener


LAST_SCAN = '{"value": [{"LastScan": ' \
            '{"Id": 1237654, "High": 0, "Medium": 1, "ScanCompletedOn": "2017-09-20T00:43:35.73+01:00"}}]}'

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
        with patch.object(url_opener.UrlOpener, 'url_read', return_value='{"access_token": "abc123"}'):
            self.__report = Checkmarx('http://url', 'username', 'password')

    def test_high_risk_warnings(self, mock_url_read):
        """ Test the number of high risk warnings. """
        mock_url_read.return_value = LAST_SCAN
        self.assertEqual(0, self.__report.nr_warnings(['id'], 'high'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')

    def test_obtain_issues(self, mock_url_read):
        """ Test that issues are correctly obtained. """
        mock_url_read.side_effect = [LAST_SCAN, '{"reportId": 22}', '{"status": {"value": "Created"}}',
                                     SAST_REPORT.format(false_positive=False, severity='High')]

        self.__report.obtain_issues(['id'], 'high')
        issues = self.__report.issues()

        self.assertIsInstance(issues, List)
        self.assertIsInstance(issues[0], Checkmarx.Issue)
        self.assertEqual('JScript Vulnerabilities', issues[0].group)
        self.assertEqual('Reflected XSS', issues[0].title)
        self.assertEqual('http://url/CxWebClient/ScanQueryDescription.aspx?queryID=789&'
                         'queryVersionCode=842956&queryTitle=Reflected_XSS', issues[0].display_url)
        self.assertEqual(1, issues[0].count)
        self.assertEqual("Recurrent", issues[0].status)

    @patch.object(logging, 'error')
    def test_obtain_issues_xml_error(self, mock_error, mock_url_read):
        """ Test that issues are correctly obtained. """
        mock_url_read.side_effect = [LAST_SCAN, '{"reportId": 22}', '{"status": {"value": "Created"}}', 'not-an-xml']
        self.__report.obtain_issues(['id'], 'high')

        issues = self.__report.issues()

        self.assertIsInstance(issues, List)
        self.assertEqual(len(issues), 0)
        self.assertEqual(mock_error.call_args[0][0], "Error in checkmarx report xml: %s.")
        self.assertIsInstance(mock_error.call_args[0][1], xml.etree.ElementTree.ParseError)

    @patch.object(logging, 'error')
    @patch.object(time, 'sleep')
    def test_obtain_issue_ssast_report_not_created(self, mock_sleep, mock_error, mock_url_read):
        """ Test that issues are correctly obtained. """
        mock_url_read.side_effect = [LAST_SCAN, '{"reportId": 22}'] + ['{"status": {"value": "InProgress"}}'] * 5
        self.__report.obtain_issues(['id'], 'high')

        issues = self.__report.issues()

        self.assertIsInstance(issues, List)
        self.assertEqual(len(issues), 0)
        mock_error.assert_called_once_with("SAST report is not created on the Checkmarx server!")
        mock_sleep.assert_called()

    @patch.object(logging, 'error')
    def test_obtain_issues_xml_tag_error(self, mock_error, mock_url_read):
        """ Test that issues are correctly obtained. """
        mock_url_read.side_effect = [LAST_SCAN, '{"reportId": 22}', '{"status": {"value": "Created"}}',
                                     '<CxXMLResults><Query /></CxXMLResults>']
        self.__report.obtain_issues(['id'], 'high')

        issues = self.__report.issues()

        self.assertIsInstance(issues, List)
        self.assertEqual(len(issues), 0)
        self.assertEqual(mock_error.call_args[0][0], "Tag %s could not be found.")
        self.assertIsInstance(mock_error.call_args[0][1], KeyError)

    def test_obtain_issues_exclude_false_positives(self, mock_url_read):
        """ Test that issues are omitted when false positive. """
        mock_url_read.side_effect = [LAST_SCAN, '{"reportId": 22}', '{"status": {"value": "Created"}}',
                                     SAST_REPORT.format(false_positive=True, severity='High')]
        self.__report.obtain_issues(['id'], 'high')
        issues = self.__report.issues()
        self.assertIsInstance(issues, List)
        self.assertEqual(len(issues), 0)

    def test_obtain_issues_exclude_wrong_severity(self, mock_url_read):
        """ Test that issues are omitted when severity does not match. """
        mock_url_read.side_effect = [LAST_SCAN, '{"reportId": 22}', '{"status": {"value": "Created"}}',
                                     SAST_REPORT.format(false_positive=False, severity='Low')]
        self.__report.obtain_issues(['id'], 'high')
        issues = self.__report.issues()
        self.assertIsInstance(issues, List)
        self.assertEqual(len(issues), 0)

    def test_obtain_issues_no_query(self, mock_url_read):
        """ Test that issues are omitted when there is no query. """
        mock_url_read.side_effect = \
            [LAST_SCAN, '{"reportId": 22}', '{"status": {"value": "Created"}}', '<CxXMLResults />']
        self.__report.obtain_issues(['id'], 'high')
        issues = self.__report.issues()
        self.assertIsInstance(issues, List)
        self.assertEqual(len(issues), 0)

    def test_obtain_issues_http_error(self, mock_url_read):
        """ Test that issues are omitted when http error occurs. """
        mock_url_read.side_effect = urllib.error.HTTPError('raise', None, None, None, None)
        self.__report.obtain_issues(['id'], 'high')
        issues = self.__report.issues()
        self.assertIsInstance(issues, List)
        self.assertEqual(len(issues), 0)

    @patch.object(logging, 'error')
    def test_obtain_issues_response_error(self, mock_error, mock_url_read):
        """ Test that issues are omitted when json error occurs. """
        mock_url_read.return_value = 'non-json'
        self.__report.obtain_issues(['id'], 'high')
        issues = self.__report.issues()
        self.assertIsInstance(issues, List)
        self.assertEqual(len(issues), 0)
        self.assertEqual(mock_error.call_args[0][0], "Error loading json: %s.")
        self.assertIsInstance(mock_error.call_args[0][1], ValueError)

    @patch.object(logging, 'error')
    def test_obtain_issues_json_error(self, mock_error, mock_url_read):
        """ Test that issues are omitted when json error occurs. """
        mock_url_read.return_value = '{}'
        self.__report.obtain_issues(['id'], 'high')
        issues = self.__report.issues()
        self.assertIsInstance(issues, List)
        self.assertEqual(len(issues), 0)
        self.assertEqual(mock_error.call_args[0][0], "Tag %s could not be found.")
        self.assertIsInstance(mock_error.call_args[0][1], KeyError)

    def test_medium_risk_warnins(self, mock_url_read):
        """ Test the number of medium risk warnings. """
        mock_url_read.return_value = LAST_SCAN
        self.assertEqual(1, self.__report.nr_warnings(['id'], 'medium'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')

    def test_passed_raise(self, mock_url_read):
        """ Test that the value is -1 when the report can't be opened. """
        mock_url_read.side_effect = urllib.error.HTTPError('raise', None, None, None, None)
        self.assertEqual(-1, self.__report.nr_warnings(['raise'], 'high'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27raise%27')

    def test_multiple_urls(self, mock_url_read):
        """ Test the number of alerts for multiple urls. """
        mock_url_read.return_value = LAST_SCAN
        self.assertEqual(2, self.__report.nr_warnings(['id1', 'id2'], 'medium'))
        self.assertEqual([
            call('http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id1%27'),
            call('http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id2%27')
        ], mock_url_read.call_args_list)

    def test_metric_source_urls_without_report(self, mock_url_read):
        """ Test the metric source urls without metric ids. """
        mock_url_read.return_value = LAST_SCAN
        self.assertEqual([], self.__report.metric_source_urls())

    def test_metric_source_urls(self, mock_url_read):
        """ Test the metric source urls with one metric id. """
        mock_url_read.return_value = LAST_SCAN
        self.assertEqual([], self.__report.metric_source_urls('id'))

    def test_metric_source_urls_on_error(self, mock_url_read):
        """ Test the metric source urls when an error occurs. """
        mock_url_read.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        self.assertEqual(["http://url/"], self.__report.metric_source_urls('project_1'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27project_1%27')

    def test_url(self, mock_url_read):
        """ Test the metric source base url. """
        mock_url_read.return_value = LAST_SCAN
        self.assertEqual("http://url/", self.__report.url())

    def test_datetime(self, mock_url_read):
        """ Test the date and time of the report. """
        mock_url_read.return_value = LAST_SCAN
        self.assertEqual(datetime.datetime(2017, 9, 20, 0, 43, 35), self.__report.datetime('id'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')

    def test_datetime_http_error(self, mock_url_read):
        """ Test the date and time of the report. """
        mock_url_read.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        self.assertEqual(datetime.datetime.min, self.__report.datetime('id'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')

    def test_datetime_missing(self, mock_url_read):
        """ Test a missing date and time of the report. """
        mock_url_read.return_value = '{"value": [{"LastScan": {}}]}'
        self.assertEqual(datetime.datetime.min, self.__report.datetime('id'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')

    def test_datetime_when_code_unchanged(self, mock_url_read):
        """ Test that the date and time of the report is the date and time of the last check when code is unchanged. """
        mock_url_read.return_value = '{"value": [{"LastScan": {"ScanCompletedOn": "2017-09-20T00:43:35.73+01:00", ' \
                                     '"Comment": "Attempt to perform scan on 9/26/2017 12:30:24 PM - No code changes ' \
                                     'were detected; "}}]}'
        self.assertEqual(datetime.datetime(2017, 9, 26, 12, 30, 24), self.__report.datetime('id'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')

    def test_datetime_when_code_unchanged_multiple_times(self, mock_url_read):
        """ Test that the date and time of the report is the date and time of the last check when code is unchanged. """
        mock_url_read.return_value = \
            '{"value": [{"LastScan": {"ScanCompletedOn": "2017-09-20T00:43:35.73+01:00", ' \
            '"Comment": "Attempt to perform scan on 9/26/2017 12:30:24 PM - No code changes ' \
            'were detected; Attempt to perform scan on 9/27/2017 12:30:24 PM - No code changes ' \
            'were detected; "}}]}'
        self.assertEqual(datetime.datetime(2017, 9, 27, 12, 30, 24), self.__report.datetime('id'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')

    def test_datetime_when_some_checks_have_no_date(self, mock_url_read):
        """ Test that the date and time of the report is the date and time of the last check when code is unchanged. """
        mock_url_read.return_value = \
            '{"value": [{"LastScan": {"ScanCompletedOn": "2016-12-14T00:01:30.737+01:00", ' \
            '"Comment": "Attempt to perform scan on 2/13/2017 8:00:06 PM - No code changes were ' \
            'detected;  No code changes were detected No code changes were detected"}}]}'
        self.assertEqual(datetime.datetime(2017, 2, 13, 20, 0, 6), self.__report.datetime('id'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')

    def test_nr_warnings_on_missing_values(self, mock_url_read):
        """ Test dealing with empty list of values. """
        mock_url_read.return_value = '{"value": []}'
        self.assertEqual(-1, self.__report.nr_warnings(['id'], 'medium'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')

    def test_datetime_on_missing_values(self, mock_url_read):
        """ Test dealing with empty list of values. """
        mock_url_read.return_value = '{"value": []}'
        self.assertEqual(datetime.datetime.min, self.__report.datetime('id'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')

    def test_datetime_on_url_exception(self, mock_url_read):
        """ Test dealing with empty list of values. """
        mock_url_read.return_value = '{"value": []}'
        self.assertEqual(datetime.datetime.min, self.__report.datetime('raise'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27raise%27')
