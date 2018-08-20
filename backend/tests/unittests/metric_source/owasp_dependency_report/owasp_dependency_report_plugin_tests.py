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
import logging
import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
import urllib.error

from hqlib import metric_source
from hqlib.metric_source import url_opener


class JenkinsOWASPDependencyReportTest(unittest.TestCase):
    """ Unit tests for the Jenkins OWASP dependency report class. """
    def setUp(self):
        self.__jenkins = metric_source.JenkinsOWASPDependencyReport(url='http://jenkins/')
        self.html = (
            '<tr>\n'
            '<tr>\n'
            '    <td class="pane">\n'
            '        <a href="file.-123/">AspNet.WebApi</a>\n'
            '    </td>\n'
            '    <td class="pane">\n'
            '        <table cellpadding="0" cellspacing="0" tooltip="High:1 - Normal:2" width="100%">\n'
            '            </tr>\n'
            '        </table>\n'
            '    </td>\n'
            '</tr>\n'
            '<tr>\n'
            '    <td class="pane">\n'
            '        <a href="file.-345/">Cors.nuspec</a>\n'
            '    </td>\n'
            '    <td class="pane">\n'
            '        <table cellpadding="0" cellspacing="0" tooltip="Normal:2" width="100%">\n'
            '            </tr>\n'
            '        </table>\n'
            '    </td>\n'
            '</tr>\n'
            '<tr>\n'
            '    <td class="pane">\n'
            '        <a href="file.-678/">Microsoft</a>\n'
            '    </td>\n'
            '    <td class="pane">\n'
            '        <table cellpadding="0" cellspacing="0" tooltip="High:1 " width="100%">\n'
            '            </tr>\n'
            '        </table>\n'
            '    </td>\n'
            '</tr>\n'
            '\n'
            '<tr>\n'
            '    <td class="pane">\n'
            '        <a href="file.-910/">Microsoft.Core</a>\n'
            '    </td>\n'
            '    <td class="pane">\n'
            '        <table cellpadding="0" cellspacing="0" tooltip="High:1" width="100%">\n'
            '            </tr>\n'
            '        </table>\n'
            '    </td>\n'
            '</tr>\n'
            '        <tr>\n'
            '    <td class="pane">\n'
            '        <a href="file.-1112/">Microsoft.AspNet.WebApi.Cors.nuspec</a>\n'
            '    </td>\n'
            '    <td class="pane">\n'
            '        <table cellpadding="0" cellspacing="0" tooltip="Normal:2" width="100%">\n'
            '            </tr>\n'
            '        </table>\n'
            '    </td>\n'
            '</tr>\n'
            '        <tr>\n'
            '    <td class="pane">\n'
            '        <a href="file.-1314/">Microsoft.AspNet.WebApi.Cors.nuspec</a>\n'
            '    </td>\n'
            '    <td class="pane">\n'
            '        <table cellpadding="0" cellspacing="0" tooltip="Normal:2" width="100%">\n'
            '            </tr>\n'
            '        </table>\n'
            '    </td>\n'
            '</tr>')
        self._cve_table_response = '''
        <table class="pane sortable" id="modules">
          <tbody>
            <tr><td class="pane"><a href="type.{type_nr}/">CVE-{cve_nr}</a></td></tr>
          </tbody>
        </table>'''

    @patch.object(url_opener.UrlOpener, 'url_open')
    def test_get_dependencies_info(self, mock_url_open):
        """ Test retrieving high priority warnings. """
        mock_url_open.side_effect = [
            self.html,
            self._cve_table_response.format(type_nr='111', cve_nr='1112'),
            self._cve_table_response.format(type_nr='234', cve_nr='2223'),
            self._cve_table_response.format(type_nr='345', cve_nr='3332')]

        result = self.__jenkins.get_dependencies_info('job', 'high')

        self.assertEqual(3, len(result))
        self.assertEqual('AspNet.WebApi', result[0].file_name)
        self.assertEqual(1, result[0].nr_vulnerabilities)
        self.assertEqual([('CVE-1112', 'http://jenkins/job/job/lastSuccessfulBuild/'
                                       'dependency-check-jenkins-pluginResult/tab.files/file.-123/type.111/HIGH')],
                         result[0].cve_links)
        self.assertEqual('Microsoft', result[1].file_name)
        self.assertEqual(1, result[1].nr_vulnerabilities)
        self.assertEqual([('CVE-2223', 'http://jenkins/job/job/lastSuccessfulBuild/'
                                       'dependency-check-jenkins-pluginResult/tab.files/file.-678/type.234/HIGH')],
                         result[1].cve_links)
        self.assertEqual('Microsoft.Core', result[2].file_name)
        self.assertEqual(1, result[2].nr_vulnerabilities)
        self.assertEqual([('CVE-3332', 'http://jenkins/job/job/lastSuccessfulBuild/'
                                       'dependency-check-jenkins-pluginResult/tab.files/file.-910/type.345/HIGH')],
                         result[2].cve_links)

    @patch.object(url_opener.UrlOpener, 'url_open')
    def test_get_dependencies_info_multiple_sources(self, mock_url_open):
        """ Test retrieving high priority warnings. """
        self.html = ''''<tr>\n'
            '    <td class="pane">\n'
            '        <a href="file.-123/">{file}</a>\n'
            '    </td>\n'
            '    <td class="pane">\n'
            '        <table cellpadding="0" cellspacing="0" tooltip="High:1" width="100%">\n'
            '            </tr>\n'
            '        </table>\n'
            '    </td>\n'
            '</tr>\n'''
        mock_url_open.side_effect = [
            self.html.format(file='AspNet.WebApi'),
            self._cve_table_response.format(type_nr='111', cve_nr='1112'),
            self.html.format(file='Other.Component'),
            self._cve_table_response.format(type_nr='222', cve_nr='2223')
        ]

        result = self.__jenkins.get_dependencies_info('job', 'high')
        result2 = self.__jenkins.get_dependencies_info('other_job', 'high')

        self.assertEqual(1, len(result))
        self.assertEqual('AspNet.WebApi', result[0].file_name)
        self.assertEqual(1, result[0].nr_vulnerabilities)
        self.assertEqual([('CVE-1112', 'http://jenkins/job/job/lastSuccessfulBuild/'
                                       'dependency-check-jenkins-pluginResult/tab.files/file.-123/type.111/HIGH')],
                         result[0].cve_links)

        self.assertEqual(1, len(result2))
        self.assertEqual('Other.Component', result2[0].file_name)
        self.assertEqual(1, result2[0].nr_vulnerabilities)
        self.assertEqual([('CVE-2223', 'http://jenkins/job/other_job/lastSuccessfulBuild/'
                                       'dependency-check-jenkins-pluginResult/tab.files/file.-123/type.222/HIGH')],
                         result2[0].cve_links)

    @patch.object(logging, 'warning')
    @patch.object(url_opener.UrlOpener, 'url_open')
    def test_get_dependencies_info_no_cves(self, mock_url_open, mock_warning):
        """ Test retrieving high priority warnings. """
        mock_url_open.side_effect = [
            '''<tr>
                <td class="pane">
                    <a href="file.-123/">AspNet.WebApi</a>
                </td>
                <td class="pane">
                    <table cellpadding="0" cellspacing="0" tooltip="High:1 - Normal:2" width="100%">
                        </tr>
                    </table>
                </td>
            </tr>''',
            '']

        result = self.__jenkins.get_dependencies_info('job', 'high')

        self.assertEqual(1, len(result))
        self.assertEqual('AspNet.WebApi', result[0].file_name)
        self.assertEqual(0, result[0].nr_vulnerabilities)
        self.assertEqual([], result[0].cve_links)
        mock_warning.assert_called_once_with(
            "No CVEs retrieved for metric_source_id %s and priority %s!", 'job', 'high')

    @patch.object(logging, 'warning')
    @patch.object(url_opener.UrlOpener, 'url_open')
    def test_get_dependencies_info_http_error(self, mock_url_open, mock_warning):
        """ Test retrieving warnings returns -1 when http error occurs. """
        mock_url_open.side_effect = urllib.error.HTTPError(None, None, None, None, None)

        self.assertEqual([], self.__jenkins.get_dependencies_info('job', 'high'))
        mock_warning.assert_called_once()
        self.assertEqual("Couldn't open %s to read warning count %s: %s", mock_warning.call_args[0][0])
        self.assertEqual("http://jenkins/job/job/lastSuccessfulBuild/dependency-check-jenkins-pluginResult/tab.files/",
                         mock_warning.call_args[0][1])
        self.assertEqual("high", mock_warning.call_args[0][2])
        self.assertIsInstance(mock_warning.call_args[0][3], urllib.error.HTTPError)

    @patch.object(url_opener.UrlOpener, 'url_open')
    def test_high_priority_warnings(self, mock_url_open):
        """ Test retrieving high priority warnings. """
        mock_url_open.return_value = self.html
        self.assertEqual(3, self.__jenkins.nr_warnings(('job',), 'high'))

    @patch.object(url_opener.UrlOpener, 'url_open')
    def test_normal_priority_warnings(self, mock_url_open):
        """ Test retrieving normal priority warnings. """
        mock_url_open.return_value = self.html
        self.assertEqual(4, self.__jenkins.nr_warnings(('job',), 'normal'))

    @patch.object(url_opener.UrlOpener, 'url_open')
    def test_low_priority_warnings(self, mock_url_open):
        """ Test retrieving low priority warnings. """
        mock_url_open.return_value = self.html
        self.assertEqual(0, self.__jenkins.nr_warnings(('job',), 'low'))

    def test_url(self):
        """ Test the url for a OWASP dependency report. """
        self.assertEqual(['http://jenkins/job/job_name/lastSuccessfulBuild/dependency-check-jenkins-pluginResult/'],
                         self.__jenkins.metric_source_urls('job_name'))

    @patch.object(url_opener.UrlOpener, 'url_open')
    def test_http_error(self, mock_url_open):
        """ Test that the default is returned when a HTTP error occurs. """
        mock_url_open.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        self.assertEqual(-1, self.__jenkins.nr_warnings(('job',), 'normal'))

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_datetime_http_error(self, mock_url_read):
        """ Test that the age of the job is returned. """
        mock_url_read.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        self.assertEqual(datetime.min, self.__jenkins.datetime(*('job',)))

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_datetime(self, mock_url_read):
        """ Test that the age of the job is returned. """
        mock_url_read.return_value = '''{"timestamp":1534268940906}'''
        self.assertEqual(
            datetime.fromtimestamp(1534268940906 / 1000) - timedelta(
                hours=(time.localtime().tm_hour - time.gmtime().tm_hour)), self.__jenkins.datetime(*('job',))
        )
