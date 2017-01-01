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

import re
import xml.etree.ElementTree

from .. import url_opener
from ..abstract import owasp_dependency_report
from ... import utils


class OWASPDependencyXMLReport(owasp_dependency_report.OWASPDependencyReport):
    """ Class representing OWASP dependency reports in XML format. """

    def __init__(self, url_open=None, **kwargs):
        self.__url_open = url_open or url_opener.UrlOpener(**kwargs).url_open
        super(OWASPDependencyXMLReport, self).__init__()

    def nr_warnings(self, report_urls, priority):
        assert priority in ('low', 'normal', 'high')
        if priority == 'normal':
            priority = 'medium'
        warnings = [self.__nr_warnings(report_url)[priority.capitalize()] for report_url in report_urls]
        return -1 if -1 in warnings else sum(warnings)

    @utils.memoized
    def __nr_warnings(self, report_url):
        """ Return the number of warnings of each priority in the report. """
        try:
            contents = self.__url_open(report_url).read()
        except url_opener.UrlOpener.url_open_exceptions:
            return dict(Low=-1, Medium=-1, High=-1)
        root = xml.etree.ElementTree.fromstring(contents)
        # ElementTree has no API to get the namespace so we extract it from the root tag:
        namespace = root.tag.split('}')[0][1:]
        # Using XPath, find all vulnerability nodes with a severity child node:
        severity_nodes = root.findall(".//{{{ns}}}vulnerability/{{{ns}}}severity".format(ns=namespace))
        return {priority: len([node for node in severity_nodes if node.text == priority])
                for priority in ('Low', 'Medium', 'High')}

    def metric_source_urls(self, *report_urls):
        return [re.sub(r'xml$', 'html', report_url) for report_url in report_urls]
