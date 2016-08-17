"""
Copyright 2012-2016 Ministerie van Sociale Zaken en Werkgelegenheid

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
import xml.etree.ElementTree

from ..abstract import owasp_dependency_report
from .. import url_opener


class OWASPDependencyXMLReport(owasp_dependency_report.OWASPDependencyReport,):
    """ Class representing OWASP dependency reports in XML format. """

    def __init__(self, url_open=None, *args, **kwargs):
        self.__url_open = url_open or url_opener.UrlOpener(**kwargs).url_open
        super(OWASPDependencyXMLReport, self).__init__(*args, **kwargs)

    def nr_warnings(self, report_urls, priority):
        """ Return the number of warnings in the reports with the specified priority. """
        assert priority in ('low', 'normal', 'high')
        if priority == 'normal':
            priority = 'medium'
        warnings = [self.__nr_warnings(report_url, priority.capitalize()) for report_url in report_urls]
        return -1 if -1 in warnings else sum(warnings)

    def __nr_warnings(self, report_url, priority):
        """ Return the number of warnings of the specified type in the report. """
        try:
            contents = self.__url_open(report_url).read()
        except url_opener.UrlOpener.url_open_exceptions as reason:
            logging.warn("Couldn't open %s to read warning count %s: %s", report_url, priority, reason)
            return -1
        root = xml.etree.ElementTree.fromstring(contents)
        # ElementTree has no API to get the namespace so we extract it from the root tag:
        namespace = root.tag.split('}')[0][1:]
        # Using XPath, find all vulnerability nodes with a severity child node that has the specified priority as text:
        return len(root.findall(".//{{{ns}}}vulnerability[{{{ns}}}severity='{prio}']".format(ns=namespace,
                                                                                             prio=priority)))

    def report_url(self, report_url):
        """ Return the url of the report. """
        return report_url
