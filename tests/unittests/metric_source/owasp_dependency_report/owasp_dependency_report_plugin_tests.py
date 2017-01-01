"""
Copyright 2012-2017 Ministerie van Sociale Zaken en Werkgelegenheid

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

import io
import unittest
import urllib2

from hqlib import metric_source


class JenkinsOWASPDependencyReportUnderTest(metric_source.JenkinsOWASPDependencyReport):
    # pylint: disable=too-few-public-methods
    """ Override the url_open method to return a fixed HTML fragment. """
    contents = u'{"jobs": []}'

    def url_open(self, url):  # pylint: disable=unused-argument
        """ Return the static contents or raise an exception. """
        if 'raise' in self.contents:
            raise urllib2.HTTPError(None, None, None, None, None)
        else:
            return io.StringIO(self.contents)


class JenkinsOWASPDependencyReportTest(unittest.TestCase):
    """ Unit tests for the Jenkins OWASP dependency report class. """
    def setUp(self):
        self.__jenkins = JenkinsOWASPDependencyReportUnderTest('http://jenkins/', 'username', 'password')

    def test_high_priority_warnings(self):
        """ Test retrieving high priority warnings. """
        self.__jenkins.contents = u'{"numberOfHighPriorityWarnings":2}'
        self.assertEqual(2, self.__jenkins.nr_warnings(['job'], 'high'))

    def test_normal_priority_warnings(self):
        """ Test retrieving normal priority warnings. """
        self.__jenkins.contents = u'{"numberOfNormalPriorityWarnings":4}'
        self.assertEqual(4, self.__jenkins.nr_warnings(['job'], 'normal'))

    def test_low_priority_warnings(self):
        """ Test retrieving low priority warnings. """
        self.__jenkins.contents = u'{"numberOfLowPriorityWarnings":9}'
        self.assertEqual(9, self.__jenkins.nr_warnings(['job'], 'low'))

    def test_url(self):
        """ Test the url for a OWASP dependency report. """
        self.assertEqual(['http://jenkins/job/job_name/lastSuccessfulBuild/dependency-check-jenkins-pluginResult/'],
                         self.__jenkins.metric_source_urls('job_name'))

    def test_http_error(self):
        """ Test that the default is returned when a HTTP error occurs. """
        self.__jenkins.contents = 'raise'
        self.assertEqual(-1, self.__jenkins.nr_warnings(['job'], 'normal'))
