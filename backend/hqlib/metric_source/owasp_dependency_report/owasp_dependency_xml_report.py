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
import functools
import re
import xml.etree.cElementTree
from typing import List, Tuple, Any

from .. import url_opener
from ..abstract import owasp_dependency_report
from ...typing import DateTime


class OWASPDependencyXMLReport(owasp_dependency_report.OWASPDependencyReport):
    """ Class representing OWASP dependency reports in XML format. """

    def __init__(self, url_read=None, **kwargs) -> None:
        self.__url_read = url_read or url_opener.UrlOpener(**kwargs).url_read
        super().__init__()

    def _nr_warnings(self, metric_source_id: str, priority: str) -> int:
        """ Return the number of warnings for the specified priority in the report. """
        if priority == 'normal':
            priority = 'medium'
        try:
            root, namespace = self.__report_root(metric_source_id)
        except url_opener.UrlOpener.url_open_exceptions:
            return -1

        dependencies = root.findall(".//{{{ns}}}dependency".format(ns=namespace))
        return len(self.__vulnerable_dependencies(dependencies, priority, namespace))

    @staticmethod
    def __vulnerable_dependencies(dependencies, priority, namespace):
        """ Return the vulnerable dependencies. """
        severity_xpath = ".//{{{ns}}}vulnerability/{{{ns}}}severity".format(ns=namespace)
        file_path_xpath = "./{{{ns}}}filePath".format(ns=namespace)

        vulnerable_dependencies: List = []

        for node in dependencies:
            severities = node.findall(severity_xpath)

            # Collect severity nodes matching 'priority'
            relevant_severities = []
            for severity in severities:
                if severity.text == priority.capitalize():
                    relevant_severities.append(severity.text)

            # For nodes matching 'priority'; append filePath to vulnerable_dependencies
            if relevant_severities:
                file_path_node_list = node.findall(file_path_xpath)
                for file_path_node in file_path_node_list:
                    file_path = file_path_node.text
                    if file_path not in vulnerable_dependencies:
                        vulnerable_dependencies.append(file_path)

        return vulnerable_dependencies

    def metric_source_urls(self, *report_urls: str) -> List[str]:
        return [re.sub(r'xml$', 'html', report_url) for report_url in report_urls]

    def _report_datetime(self, metric_source_id: str) -> DateTime:
        """ Return the report date and time. """
        try:
            root, namespace = self.__report_root(metric_source_id)
        except url_opener.UrlOpener.url_open_exceptions:
            return datetime.datetime.min
        datetime_node = root.find(".//{{{ns}}}projectInfo/{{{ns}}}reportDate".format(ns=namespace))
        return datetime.datetime.strptime(datetime_node.text.split('.')[0], "%Y-%m-%dT%H:%M:%S")

    @functools.lru_cache(maxsize=1024)
    def __report_root(self, report_url: str) -> Tuple[Any, str]:
        """ Return the root node and namespace of the OWASP dependency XML report. """
        contents = self.__url_read(report_url)
        root = xml.etree.cElementTree.fromstring(contents)
        # ElementTree has no API to get the namespace so we extract it from the root tag:
        namespace = root.tag.split('}')[0][1:]
        return root, namespace
