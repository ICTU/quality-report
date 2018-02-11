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

import datetime
import io
import unittest
import urllib.error
from typing import cast, IO

from hqlib import metric_source


class JenkinsOWASPDependencyReportUnderTest(metric_source.JenkinsOWASPDependencyReport):
    # pylint: disable=too-few-public-methods
    """ Override the url_open method to return a fixed HTML fragment. """
    contents = '{"jobs": []}'
    html = (
        '<tr>\n'
        '<tr>\n'
        '    <td class="pane">\n'
        '        <a href="file.-1840927159/">Microsoft.AspNet.WebApi.Cors.nuspec</a>\n'
        '    </td>\n'
        '    <td class="pane">\n'
        '        <table cellpadding="0" cellspacing="0" tooltip="High:1 - Normal:2" width="100%">\n'
        '            </tr>\n'
        '        </table>\n'
        '    </td>\n'
        '</tr>\n'
        '<tr>\n'
        '    <td class="pane">\n'
        '        <a href="file.-1840927159/">Microsoft.AspNet.WebApi.Cors.nuspec</a>\n'
        '    </td>\n'
        '    <td class="pane">\n'
        '        <table cellpadding="0" cellspacing="0" tooltip="Normal:2" width="100%">\n'
        '            </tr>\n'
        '        </table>\n'
        '    </td>\n'
        '</tr>\n'
        '<tr>\n'
        '    <td class="pane">\n'
        '        <a href="file.-92822313/">Microsoft.AspNet.WebApi.Core.nuspec</a>\n'
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
        '        <a href="file.-1840927159/">Microsoft.AspNet.WebApi.Cors.nuspec</a>\n'
        '    </td>\n'
        '    <td class="pane">\n'
        '        <table cellpadding="0" cellspacing="0" tooltip="High:1width="100%">\n'
        '            </tr>\n'
        '        </table>\n'
        '    </td>\n'
        '</tr>\n'
        '        <tr>\n'
        '    <td class="pane">\n'
        '        <a href="file.-1840927159/">Microsoft.AspNet.WebApi.Cors.nuspec</a>\n'
        '    </td>\n'
        '    <td class="pane">\n'
        '        <table cellpadding="0" cellspacing="0" tooltip="Normal:2" width="100%">\n'
        '            </tr>\n'
        '        </table>\n'
        '    </td>\n'
        '</tr>\n'
        '        <tr>\n'
        '    <td class="pane">\n'
        '        <a href="file.-1840927159/">Microsoft.AspNet.WebApi.Cors.nuspec</a>\n'
        '    </td>\n'
        '    <td class="pane">\n'
        '        <table cellpadding="0" cellspacing="0" tooltip="Normal:2" width="100%">\n'
        '            </tr>\n'
        '        </table>\n'
        '    </td>\n'
        '</tr>')

    def url_read(self, url: str, *args, encoding: str = 'utf-8', **kwargs) -> str:  # pylint: disable=unused-argument
        """ Return the static contents. """
        return self.contents

    def url_open(self, url: str, log_error: bool = True) -> IO:  # pylint: disable=unused-argument
        return cast(IO, io.StringIO(self.html))

    def _get_soup(self, url: str):
        """ Get a beautiful soup of the HTML at the url. """
        if 'raise' in self.contents:
            raise urllib.error.HTTPError(None, None, None, None, None)
        else:
            return super()._get_soup(url)


class JenkinsOWASPDependencyReportTest(unittest.TestCase):
    """ Unit tests for the Jenkins OWASP dependency report class. """
    def setUp(self):
        JenkinsOWASPDependencyReportUnderTest._api.cache_clear()
        JenkinsOWASPDependencyReportUnderTest.nr_warnings.cache_clear()
        self.__jenkins = JenkinsOWASPDependencyReportUnderTest('http://jenkins/', 'username', 'password')
        self.html = (
            '<tr>\n'
            '<tr>\n'
            '    <td class="pane">\n'
            '        <a href="file.-1840927159/">Microsoft.AspNet.WebApi.Cors.nuspec</a>\n'
            '    </td>\n'
            '    <td class="pane">\n'
            '        <table cellpadding="0" cellspacing="0" tooltip="High:1 - Normal:2" width="100%">\n'
            '            </tr>\n'
            '        </table>\n'
            '    </td>\n'
            '</tr>\n'
            '<tr>\n'
            '    <td class="pane">\n'
            '        <a href="file.-1840927159/">Microsoft.AspNet.WebApi.Cors.nuspec</a>\n'
            '    </td>\n'
            '    <td class="pane">\n'
            '        <table cellpadding="0" cellspacing="0" tooltip="Normal:2" width="100%">\n'
            '            </tr>\n'
            '        </table>\n'
            '    </td>\n'
            '</tr>\n'
            '<tr>\n'
            '    <td class="pane">\n'
            '        <a href="file.-92822313/">Microsoft.AspNet.WebApi.Core.nuspec</a>\n'
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
            '        <a href="file.-1840927159/">Microsoft.AspNet.WebApi.Cors.nuspec</a>\n'
            '    </td>\n'
            '    <td class="pane">\n'
            '        <table cellpadding="0" cellspacing="0" tooltip="High:1width="100%">\n'
            '            </tr>\n'
            '        </table>\n'
            '    </td>\n'
            '</tr>\n'
            '        <tr>\n'
            '    <td class="pane">\n'
            '        <a href="file.-1840927159/">Microsoft.AspNet.WebApi.Cors.nuspec</a>\n'
            '    </td>\n'
            '    <td class="pane">\n'
            '        <table cellpadding="0" cellspacing="0" tooltip="Normal:2" width="100%">\n'
            '            </tr>\n'
            '        </table>\n'
            '    </td>\n'
            '</tr>\n'
            '        <tr>\n'
            '    <td class="pane">\n'
            '        <a href="file.-1840927159/">Microsoft.AspNet.WebApi.Cors.nuspec</a>\n'
            '    </td>\n'
            '    <td class="pane">\n'
            '        <table cellpadding="0" cellspacing="0" tooltip="Normal:2" width="100%">\n'
            '            </tr>\n'
            '        </table>\n'
            '    </td>\n'
            '</tr>')

    def test_high_priority_warnings(self):
        """ Test retrieving high priority warnings. """
        self.__jenkins.contents = self.html
        self.assertEqual(3, self.__jenkins.nr_warnings(('job',), 'high'))

    def test_normal_priority_warnings(self):
        """ Test retrieving normal priority warnings. """
        self.__jenkins.contents = self.html
        self.assertEqual(4, self.__jenkins.nr_warnings(('job',), 'normal'))

    def test_low_priority_warnings(self):
        """ Test retrieving low priority warnings. """
        self.__jenkins.contents = self.html
        self.assertEqual(0, self.__jenkins.nr_warnings(('job',), 'low'))

    def test_url(self):
        """ Test the url for a OWASP dependency report. """
        self.assertEqual(['http://jenkins/job/job_name/lastSuccessfulBuild/dependency-check-jenkins-pluginResult/'],
                         self.__jenkins.metric_source_urls('job_name'))

    def test_http_error(self):
        """ Test that the default is returned when a HTTP error occurs. """
        self.__jenkins.contents = 'raise'
        self.assertEqual(-1, self.__jenkins.nr_warnings(('job',), 'normal'))

    def test_datetime(self):
        """ Test that the age of the job is returned. """
        self.assertEqual(datetime.datetime.min, self.__jenkins.datetime(*('job',)))
