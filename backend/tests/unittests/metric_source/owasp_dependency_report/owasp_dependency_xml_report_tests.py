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
from unittest.mock import patch
import urllib.error
from hqlib import metric_source


@patch.object(metric_source.url_opener.UrlOpener, 'url_read')
class OWASPDependencyXMLReportTest(unittest.TestCase):
    """ Unit tests for the OWASP dependency XML report class. """

    def setUp(self):
        metric_source.OWASPDependencyXMLReport._OWASPDependencyXMLReport__report_root.cache_clear()
        metric_source.OWASPDependencyXMLReport.nr_warnings.cache_clear()
        self.__report = metric_source.OWASPDependencyXMLReport()

    def test_get_dependencies_info_normal(self, mock_url_read):
        """ Test that it gets medium priority warnings. """
        mock_url_read.return_value = '''
        <analysis xmlns="https://namespace.1.3.xsd">
            <dependencies>
              <dependency />
              <dependency>
                <fileName>dependency.name</fileName>
                <description>Desc.</description>
                <vulnerabilities>
                  <vulnerability>
                    <name>CVE-123</name>
                    <severity>Medium</severity>
                    <references>
                      <reference><url>http://www.securityfocus.com/bid/123</url></reference>
                    </references>
                  </vulnerability>
                  <vulnerability>
                    <name>CVE-124</name>
                    <severity>Medium</severity>
                    <references>
                      <reference><url>http://www.securityfocus.com/bid/124</url></reference>
                    </references>
                  </vulnerability>
                </vulnerabilities>
              </dependency>
            </dependencies>
        </analysis>'''

        result = self.__report.get_dependencies_info('url', 'normal')

        self.assertEqual('dependency.name', result[0].file_name)
        self.assertEqual(2, result[0].nr_vulnerabilities)
        self.assertEqual([('CVE-123', 'http://www.securityfocus.com/bid/123'),
                          ('CVE-124', 'http://www.securityfocus.com/bid/124')], result[0].cve_links)

    def test_get_dependencies_info_high(self, mock_url_read):
        """ Test that it gets only dependencies with high priority warnings. """
        mock_url_read.return_value = '''
        <analysis xmlns="https://namespace.1.3.xsd">
            <dependencies>
              <dependency>
                <fileName>dependency.name</fileName>
                <description>Desc.</description>
                <vulnerabilities>
                  <vulnerability>
                    <name>CVE-123</name>
                    <severity>High</severity>
                    <references>
                      <reference><url>http://www.securityfocus.com/bid/123</url></reference>
                    </references>
                  </vulnerability>
                  <vulnerability>
                    <name>CVE-124</name>
                    <severity>Medium</severity>
                    <references>
                      <reference><url>http://www.securityfocus.com/bid/124</url></reference>
                    </references>
                  </vulnerability>
                </vulnerabilities>
              </dependency>
            </dependencies>
        </analysis>'''

        result = self.__report.get_dependencies_info('url', 'whatever, not normal!')

        self.assertEqual('dependency.name', result[0].file_name)
        self.assertEqual(1, result[0].nr_vulnerabilities)
        self.assertEqual([('CVE-123', 'http://www.securityfocus.com/bid/123')], result[0].cve_links)

    @patch.object(logging, 'error')
    def test_get_dependencies_info_http_error(self, mock_error, mock_url_read):
        """ Test that it returns empty list and logs event, with http error occurs. """
        mock_url_read.side_effect = urllib.error.HTTPError(None, None, None, None, None)

        result = self.__report.get_dependencies_info('url', 'x')

        self.assertEqual([], result)
        mock_error.assert_called_once_with('Error retrieving dependencies information for %s, priority %s.',
                                           'url', 'High')

    def test_high_priority_warnings(self, mock_url_read):
        """ Test retrieving high priority warnings. """
        mock_url_read.return_value = '''<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.1.3.xsd">
            <dependencies>
                <dependency>
                <filePath>testHigh</filePath>
                    <vulnerabilities>
                        <vulnerability>
                            <severity>High</severity>
                        </vulnerability>
                    </vulnerabilities>
                    <relatedDependencies>
                        <relatedDependency>
                            <filePath>/tmp/src/packaging/target/vib/WEB-INF/lib/vib-services-soap-client-11.0.234.jar</filePath>
                            <sha1>93622cad52550fa7b5dd186ae8bddd10c16df215</sha1>
                            <md5>5bb4f244edd7d043507432e76e804581</md5>
                            <identifier type="maven">
                                <name>(nl.ictu.isr.templates:vib-services-soap-client:11.0.234)</name>
                            </identifier>
                         </relatedDependency>
                    </relatedDependencies>

                </dependency>
            </dependencies>
        </analysis>
        '''
        self.assertEqual(1, self.__report.nr_warnings(('url',), 'high'))

    def test_normal_priority_warnings(self, mock_url_read):
        """ Test retrieving normal priority warnings. """
        mock_url_read.return_value = '''<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.1.3.xsd">
            <dependencies>
                <dependency>
                <relatedDependencies>
                <relatedDependency>
                    <filePath>/tmp/src/packaging/target/vib/WEB-INF/lib/vib-services-soap-client-11.0.234.jar</filePath>
                    <sha1>93622cad52550fa7b5dd186ae8bddd10c16df215</sha1>
                    <md5>5bb4f244edd7d043507432e76e804581</md5>
                    <identifier type="maven">
                        <name>(nl.ictu.isr.templates:vib-services-soap-client:11.0.234)</name>
                    </identifier>
                </relatedDependency>
                </relatedDependencies>
                <filePath>testNormal</filePath>
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
                <dependency>
                <filePath>testNormal2</filePath>
                    <vulnerabilities>
                        <vulnerability>
                            <severity>High</severity>
                        </vulnerability>
                         <vulnerability>
                            <severity>Medium</severity>
                        </vulnerability>
                    </vulnerabilities>
                    <relatedDependencies>
                    <relatedDependency>
                        <filePath>/tmp/src/packaging/target/vib/WEB-INF/lib/vib-services-soap-client-11.0.234.jar</filePath>
                        <sha1>93622cad52550fa7b5dd186ae8bddd10c16df215</sha1>
                        <md5>5bb4f244edd7d043507432e76e804581</md5>
                        <identifier type="maven">
                            <name>(nl.ictu.isr.templates:vib-services-soap-client:11.0.234)</name>
                        </identifier>
                    </relatedDependency>
                    </relatedDependencies>
                </dependency>
            </dependencies>
        </analysis>
        '''
        self.assertEqual(2, self.__report.nr_warnings(('url',), 'normal'))

    def test_low_priority_warnings(self, mock_url_read):
        """ Test retrieving low priority warnings. """
        mock_url_read.return_value = '''<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.1.3.xsd">
            <dependencies>
                <dependency>
                <filePath>testLow</filePath>
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
                <dependency>
                <filePath>testLow2</filePath>
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
                <dependency>
                <filePath>testLow3</filePath>
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
                <dependency>
                <filePath>testLow4</filePath>
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
                    <relatedDependencies>
                        <relatedDependency>
                            <filePath>/tmp/src/packaging/target/vib/WEB-INF/lib/vib-services-soap-client-11.0.234.jar</filePath>
                            <sha1>93622cad52550fa7b5dd186ae8bddd10c16df215</sha1>
                            <md5>5bb4f244edd7d043507432e76e804581</md5>
                            <identifier type="maven">
                                <name>(nl.ictu.isr.templates:vib-services-soap-client:11.0.234)</name>
                            </identifier>
                        </relatedDependency>
                    </relatedDependencies>
                </dependency>
            </dependencies>
        </analysis>
        '''
        self.assertEqual(4, self.__report.nr_warnings(('url', ), 'low'))

    def test_url(self, mock_url_read):
        """ Test the url for a OWASP dependency report. """
        self.assertEqual(['http://url/'], self.__report.metric_source_urls('http://url/'))
        mock_url_read.assert_not_called()

    def test_http_error(self, mock_url_read):
        """ Test that the default is returned when a HTTP error occurs. """
        mock_url_read.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        self.assertEqual(-1, self.__report.nr_warnings(('url',), 'normal'))

    def test_datetime(self, mock_url_read):
        """ Test that the date time is correctly parsed from the report. """
        mock_url_read.return_value = '''<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.1.3.xsd">
            <projectInfo>
                <name>generic</name>
                <reportDate>2017-02-10T15:29:30.600+0000</reportDate>
                <credits>...</credits>
            </projectInfo>
        </analysis>
        '''
        self.assertEqual(datetime.datetime(2017, 2, 10, 15, 29, 30), self.__report.datetime('url'))

    def test_datetime_on_error(self, mock_url_read):
        """ Test that the date time is the minimum date/time when an error occurs. """
        mock_url_read.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        self.assertEqual(datetime.datetime.min, self.__report.datetime('url'))
