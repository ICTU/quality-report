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

import os
import logging
import zipfile
import urllib.error
import xml.etree.cElementTree
import unittest
from unittest.mock import MagicMock, patch

from hqlib import metric_source
from hqlib.metric_source import url_opener


class TfsOWASPDependencyXMLReportTest(unittest.TestCase):
    """ Unit tests for the TFS OWASP dependency XML report class. """

    def setUp(self):
        # pylint: disable=protected-access
        # pylint: disable=no-member
        metric_source.OWASPDependencyXMLReport._OWASPDependencyXMLReport__report_root.cache_clear()
        metric_source.OWASPDependencyXMLReport.nr_warnings.cache_clear()

    @patch.object(url_opener.UrlOpener, 'url_read')
    @patch.object(url_opener.UrlOpener, 'url_open')
    def test_get_dependencies_info(self, mock_url_open, mock_url_read):
        """ Test that it gets medium priority warnings. """
        mock_url_read.return_value = '{"value": [{"url": "http://build"}]}'
        archive = zipfile.ZipFile('temp.zip', 'w')
        report = '''<analysis xmlns="https://namespace.1.3.xsd">
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
        archive.writestr(os.path.join('OWASP', 'dependency-check-report.xml'), report)
        archive.close()

        with open('temp.zip', 'rb') as disk_file:
            byte_stream = disk_file.read()
        os.remove('temp.zip')

        response = MagicMock()
        response.read = MagicMock(return_value=byte_stream)

        mock_url_open.return_value = response

        report = metric_source.TfsOWASPDependencyXMLReport(
            base_url='http://base.url', organization='org', project='Project',
            definitions='2,3', pat_token='abc3_pat_token')

        result = report.get_dependencies_info('url', 'normal')

        self.assertEqual('dependency.name', result[0].file_name)
        self.assertEqual(2, result[0].nr_vulnerabilities)
        self.assertEqual([('CVE-123', 'http://www.securityfocus.com/bid/123'),
                          ('CVE-124', 'http://www.securityfocus.com/bid/124')], result[0].cve_links)

    @patch.object(url_opener.UrlOpener, 'url_read')
    @patch.object(url_opener.UrlOpener, 'url_open')
    def test_nr_warnings(self, mock_url_open, mock_url_read):
        """ Test retrieving high priority warnings. """
        mock_url_read.return_value = '{"value": [{"url": "http://build"}]}'
        archive = zipfile.ZipFile('temp.zip', 'w')
        report = '''<?xml version="1.0"?>
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
        archive.writestr(os.path.join('OWASP', 'dependency-check-report.xml'), report)
        archive.close()

        with open('temp.zip', 'rb') as disk_file:
            byte_stream = disk_file.read()
        os.remove('temp.zip')

        response = MagicMock()
        response.read = MagicMock(return_value=byte_stream)

        mock_url_open.return_value = response

        report = metric_source.TfsOWASPDependencyXMLReport(
            base_url='http://base.url', organization='org', project='Project',
            definitions='2,3', pat_token='abc3_pat_token')

        self.assertEqual(1, report.nr_warnings(('url',), 'high'))

    @patch.object(logging, 'error')
    @patch.object(url_opener.UrlOpener, 'url_read')
    @patch.object(url_opener.UrlOpener, 'url_open')
    def test_nr_warnings_http_error(self, mock_url_open, mock_url_read, mock_error):
        """ Test retrieving high priority warnings. """
        mock_url_read.return_value = '{"value": [{"url": "http://build"}]}'
        mock_url_open.side_effect = urllib.error.HTTPError(None, None, None, None, None)

        report = metric_source.TfsOWASPDependencyXMLReport(
            base_url='http://base.url', organization='org', project='Project',
            definitions='2,3', pat_token='abc3_pat_token')

        self.assertEqual(-1, report.nr_warnings(('url',), 'high'))
        self.assertEqual('Error getting content of the OWASP report from %s.', mock_error.mock_calls[0][1][0])
        self.assertEqual(mock_error.mock_calls[0][1][1],
                         'http://build/artifacts?artifactName=OWASP&api-version=4.1&%24format=zip')
        self.assertEqual('Error parsing returned xml: %s.', mock_error.mock_calls[1][1][0])
        self.assertIsInstance(mock_error.mock_calls[1][1][1], xml.etree.ElementTree.ParseError)

    @patch.object(logging, 'error')
    @patch.object(url_opener.UrlOpener, 'url_read')
    @patch.object(url_opener.UrlOpener, 'url_open')
    def test_nr_warnings_unreadable_content(self, mock_url_open, mock_url_read, mock_error):
        """ Test retrieving high priority warnings. """
        mock_url_read.return_value = '{"value": [{"url": "http://build"}]}'
        mock_url_open.return_value = 'not an object with read function'

        report = metric_source.TfsOWASPDependencyXMLReport(
            base_url='http://base.url', organization='org', project='Project',
            definitions='2,3', pat_token='abc3_pat_token')

        self.assertEqual(-1, report.nr_warnings(('url',), 'high'))
        self.assertEqual("Error reading server response of the OWASP report: %s.", mock_error.mock_calls[0][1][0])
        self.assertIsInstance(mock_error.mock_calls[0][1][1], AttributeError)
        self.assertEqual('Error parsing returned xml: %s.', mock_error.mock_calls[1][1][0])
        self.assertIsInstance(mock_error.mock_calls[1][1][1], xml.etree.ElementTree.ParseError)

    @patch.object(logging, 'error')
    @patch.object(url_opener.UrlOpener, 'url_read')
    @patch.object(url_opener.UrlOpener, 'url_open')
    def test_nr_warnings_unexpected_content_type(self, mock_url_open, mock_url_read, mock_error):
        """ Test retrieving high priority warnings. """
        mock_url_read.return_value = '{"value": [{"url": "http://build"}]}'
        response = MagicMock()
        response.read = MagicMock(return_value='unexpected content')
        mock_url_open.return_value = response

        report = metric_source.TfsOWASPDependencyXMLReport(
            base_url='http://base.url', organization='org', project='Project',
            definitions='2,3', pat_token='abc3_pat_token')

        self.assertEqual(-1, report.nr_warnings(('url',), 'high'))
        self.assertEqual("Error casting server response for the OWASP report to a byte stream: %s.",
                         mock_error.mock_calls[0][1][0])
        self.assertIsInstance(mock_error.mock_calls[0][1][1], TypeError)
        self.assertEqual('Error parsing returned xml: %s.', mock_error.mock_calls[1][1][0])
        self.assertIsInstance(mock_error.mock_calls[1][1][1], xml.etree.ElementTree.ParseError)

    @patch.object(logging, 'error')
    @patch.object(url_opener.UrlOpener, 'url_read')
    @patch.object(url_opener.UrlOpener, 'url_open')
    def test_nr_warnings_corrupted_archive(self, mock_url_open, mock_url_read, mock_error):
        """ Test retrieving high priority warnings. """
        mock_url_read.return_value = '{"value": [{"url": "http://build"}]}'
        response = MagicMock()
        response.read = MagicMock(return_value=b'unexpected content')
        mock_url_open.return_value = response

        report = metric_source.TfsOWASPDependencyXMLReport(
            base_url='http://base.url', organization='org', project='Project',
            definitions='2,3', pat_token='abc3_pat_token')

        self.assertEqual(-1, report.nr_warnings(('url',), 'high'))
        self.assertEqual("Archive of the OWASP report is corrupted: %s.", mock_error.mock_calls[0][1][0])
        self.assertIsInstance(mock_error.mock_calls[0][1][1], zipfile.BadZipFile)
        self.assertEqual('Error parsing returned xml: %s.', mock_error.mock_calls[1][1][0])
        self.assertIsInstance(mock_error.mock_calls[1][1][1], xml.etree.ElementTree.ParseError)

    @patch.object(logging, 'error')
    @patch.object(url_opener.UrlOpener, 'url_read')
    @patch.object(url_opener.UrlOpener, 'url_open')
    def test_nr_warnings_no_archived_content(self, mock_url_open, mock_url_read, mock_error):
        """ Test retrieving high priority warnings. """
        mock_url_read.return_value = '{"value": [{"url": "http://build"}]}'

        archive = zipfile.ZipFile('temp.zip', 'w')
        report = 'some content'
        archive.writestr('zipped_file.txt', report)
        archive.close()

        with open('temp.zip', 'rb') as disk_file:
            byte_stream = disk_file.read()
        os.remove('temp.zip')

        response = MagicMock()
        response.read = MagicMock(return_value=byte_stream)
        mock_url_open.return_value = response

        report = metric_source.TfsOWASPDependencyXMLReport(
            base_url='http://base.url', organization='org', project='Project',
            definitions='2,3', pat_token='abc3_pat_token')

        self.assertEqual(-1, report.nr_warnings(('url',), 'high'))
        self.assertEqual("Archive of the OWASP report is corrupted: %s.", mock_error.mock_calls[0][1][0])
        self.assertIsInstance(mock_error.mock_calls[0][1][1], KeyError)
        self.assertEqual('Error parsing returned xml: %s.', mock_error.mock_calls[1][1][0])
        self.assertIsInstance(mock_error.mock_calls[1][1][1], xml.etree.ElementTree.ParseError)

    @patch.object(logging, 'error')
    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_constructor_http_error(self, mock_url_read, mock_error):
        """ Test constructor when http error occurs. """
        mock_url_read.side_effect = urllib.error.HTTPError(None, None, None, None, None)

        result = metric_source.TfsOWASPDependencyXMLReport(
            base_url='http://base.url', organization='org', project='Project',
            definitions='2,3', pat_token='abc3_pat_token')

        self.assertIsNotNone(result)
        mock_error.assert_called_once_with(
            'Error constructing TfsOWASPDependencyXMLReport - could not get list of builds.')

    @patch.object(logging, 'error')
    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_constructor_json_error(self, mock_url_read, mock_error):
        """ Test constructor when invalid json returned. """
        mock_url_read.return_value = 'non-json'

        result = metric_source.TfsOWASPDependencyXMLReport(
            base_url='http://base.url', organization='org', project='Project',
            definitions='2,3', pat_token='abc3_pat_token')

        self.assertIsNotNone(result)
        mock_error.assert_called_with(
            'Error constructing TfsOWASPDependencyXMLReport - JSON error.')

    @patch.object(logging, 'error')
    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_constructor_json_key_error(self, mock_url_read, mock_error):
        """ Test constructor when invalid json returned. """
        mock_url_read.return_value = '{"value": [{"not_url": "xxx"}]}'

        result = metric_source.TfsOWASPDependencyXMLReport(
            base_url='http://base.url', organization='org', project='Project',
            definitions='2,3', pat_token='abc3_pat_token')

        self.assertIsNotNone(result)
        self.assertEqual("Error constructing TfsOWASPDependencyXMLReport - JSON error: %s.",
                         mock_error.mock_calls[0][1][0])
        self.assertIsInstance(mock_error.mock_calls[0][1][1], KeyError)
