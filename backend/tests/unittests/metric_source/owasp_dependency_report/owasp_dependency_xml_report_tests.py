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
import unittest
import urllib.error

from hqlib import metric_source


class OWASPDependencyXMLReportTest(unittest.TestCase):
    """ Unit tests for the OWASP dependency XML report class. """
    contents = ''

    def setUp(self):
        metric_source.OWASPDependencyXMLReport._OWASPDependencyXMLReport__report_root.cache_clear()
        metric_source.OWASPDependencyXMLReport.nr_warnings.cache_clear()
        self.__report = metric_source.OWASPDependencyXMLReport(url_read=self.__url_read)

    def __url_read(self, url):  # pylint: disable=unused-argument
        """ Return the static contents or raise an exception. """
        if 'raise' in self.contents:
            raise urllib.error.HTTPError(None, None, None, None, None)
        else:
            return self.contents

    def test_high_priority_warnings(self):
        """ Test retrieving high priority warnings. """
        self.contents = '''<?xml version="1.0"?>
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

    def test_normal_priority_warnings(self):
        """ Test retrieving normal priority warnings. """
        self.contents = '''<?xml version="1.0"?>
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

    def test_low_priority_warnings(self):
        """ Test retrieving low priority warnings. """
        self.contents = '''<?xml version="1.0"?>
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

    def test_url(self):
        """ Test the url for a OWASP dependency report. """
        self.assertEqual(['http://url/'], self.__report.metric_source_urls('http://url/'))

    def test_http_error(self):
        """ Test that the default is returned when a HTTP error occurs. """
        self.contents = 'raise'
        self.assertEqual(-1, self.__report.nr_warnings(('url',), 'normal'))

    def test_datetime(self):
        """ Test that the date time is correctly parsed from the report. """
        self.contents = '''<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.1.3.xsd">
            <projectInfo>
                <name>generic</name>
                <reportDate>2017-02-10T15:29:30.600+0000</reportDate>
                <credits>...</credits>
            </projectInfo>
        </analysis>
        '''
        self.assertEqual(datetime.datetime(2017, 2, 10, 15, 29, 30), self.__report.datetime('url'))

    def test_datetime_on_error(self):
        """ Test that the date time is the minimum date/time when an error occurs. """
        self.contents = 'raise'
        self.assertEqual(datetime.datetime.min, self.__report.datetime('url'))
