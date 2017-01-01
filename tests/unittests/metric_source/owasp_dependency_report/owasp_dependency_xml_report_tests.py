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


class OWASPDependencyXMLReportTest(unittest.TestCase):
    """ Unit tests for the OWASP dependency XML report class. """
    contents = u''

    def setUp(self):
        self.__report = metric_source.OWASPDependencyXMLReport(url_open=self.__url_open)

    def __url_open(self, url):  # pylint: disable=unused-argument
        """ Return the static contents or raise an exception. """
        if 'raise' in self.contents:
            raise urllib2.HTTPError(None, None, None, None, None)
        else:
            return io.StringIO(self.contents)

    def test_high_priority_warnings(self):
        """ Test retrieving high priority warnings. """
        self.contents = u'''<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.1.3.xsd">
            <dependencies>
                <dependency>
                    <vulnerabilities>
                        <vulnerability>
                            <severity>High</severity>
                        </vulnerability>
                    </vulnerabilities>
                </dependency>
            </dependencies>
        </analysis>
        '''
        self.assertEqual(1, self.__report.nr_warnings(['url'], 'high'))

    def test_normal_priority_warnings(self):
        """ Test retrieving normal priority warnings. """
        self.contents = u'''<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.1.3.xsd">
            <dependencies>
                <dependency>
                    <vulnerabilities>
                        <vulnerability>
                            <severity>High</severity>
                        </vulnerability>
                         <vulnerability>
                            <severity>Medium</severity>
                        </vulnerability>
                         <vulnerability>
                            <severity>Medium</severity>
                        </vulnerability>
                    </vulnerabilities>
                </dependency>
            </dependencies>
        </analysis>
        '''
        self.assertEqual(2, self.__report.nr_warnings(['url'], 'normal'))

    def test_low_priority_warnings(self):
        """ Test retrieving low priority warnings. """
        self.contents = u'''<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.1.3.xsd">
            <dependencies>
                <dependency>
                    <vulnerabilities>
                        <vulnerability>
                            <severity>Medium</severity>
                        </vulnerability>
                         <vulnerability>
                            <severity>Low</severity>
                        </vulnerability>
                         <vulnerability>
                            <severity>Low</severity>
                        </vulnerability>
                    </vulnerabilities>
                </dependency>
            </dependencies>
        </analysis>
        '''
        self.assertEqual(4, self.__report.nr_warnings(['url', 'url'], 'low'))

    def test_url(self):
        """ Test the url for a OWASP dependency report. """
        self.assertEqual(['http://url/'], self.__report.metric_source_urls('http://url/'))

    def test_http_error(self):
        """ Test that the default is returned when a HTTP error occurs. """
        self.contents = 'raise'
        self.assertEqual(-1, self.__report.nr_warnings(['url'], 'normal'))
