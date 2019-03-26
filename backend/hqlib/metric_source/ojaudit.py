"""
Copyright 2012-2019 Ministerie van Sociale Zaken en Werkgelegenheid

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
import re
from typing import List
import xml.etree.cElementTree

from . import url_opener
from .. import domain


class OJAuditReport(domain.MetricSource):
    """ Class representing OJAudit reports. """

    metric_source_name = 'OJAudit report'

    def __init__(self, *args, **kwargs) -> None:
        self.__metric_source_url_re = kwargs.pop("metric_source_url_re", r"\.xml$")
        self.__metric_source_url_repl = kwargs.pop("metric_source_url_repl", ".html")
        self._url_read = url_opener.UrlOpener(**kwargs).url_read
        super().__init__()

    def violations(self, violation_type: str, *metric_source_ids) -> int:
        """ Return the number of violations reported by OJAudit. """
        violations = 0
        for metric_source_id in metric_source_ids:
            try:
                contents = self._url_read(metric_source_id)
            except url_opener.UrlOpener.url_open_exceptions:
                return -1
            try:
                tree = xml.etree.cElementTree.fromstring(contents)
            except xml.etree.cElementTree.ParseError as reason:
                logging.error("Couldn't parse report at %s: %s", metric_source_id, reason)
                return -1

            # ElementTree has no API to get the namespace so we extract it from the root tag:
            namespaces = dict(ns=tree.tag.split('}')[0][1:])
            violations += int(tree.findtext(f"./ns:{violation_type}-count", namespaces=namespaces))

        return violations

    def metric_source_urls(self, *report_urls: str) -> List[str]:
        return [re.sub(self.__metric_source_url_re, self.__metric_source_url_repl, report_url)
                for report_url in report_urls]
