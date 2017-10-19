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

import csv
import datetime
import logging
import re
from typing import List, Iterable

import dateutil.parser

from ..abstract import performance_report
from hqlib.metric_source import url_opener
from hqlib.typing import DateTime


class SpiritSplunkCSVPerformanceReport(performance_report.PerformanceReport, url_opener.UrlOpener):
    """ The Spirit Splunk CSV performance report is a simple CSV text file exported from Splunk. """
    PRODUCT_COLUMN = 2
    PASS_FAIL_COLUMN = 19

    def __init__(self, *args, **kwargs) -> None:
        self.__report_urls = kwargs.pop('report_urls', None)
        super().__init__(*args, **kwargs)

    def _query_rows(self, product: str) -> List:
        """ Return the queries for the specified product. """
        rows = []
        product_query_re = re.compile(product)
        for url in self.urls(product):
            for row in self.__rows(url):
                if len(row) > self.PASS_FAIL_COLUMN and product_query_re.match(row[self.PRODUCT_COLUMN]):
                    rows.append(row)
        return rows

    def _has_query_color(self, row, color) -> bool:
        """ Return whether the query has the specified color. """
        if color in ('yellow', 'red'):
            return row[self.PASS_FAIL_COLUMN] == 'Failed'
        else:
            return row[self.PASS_FAIL_COLUMN] != 'Failed'

    def _datetime_from_url(self, url) -> DateTime:
        """ Return the date when performance was last measured. """
        try:
            rows = self.__rows(url)
        except url_opener.UrlOpener.url_open_exceptions:
            return datetime.datetime.min
        try:
            return dateutil.parser.parse(list(rows)[1][10].split(' ')[0], dayfirst=True)
        except (ValueError, IndexError, TypeError) as reason:
            logging.error("Couldn't parse report date time from %s, retrieved from %s: %s", rows, url, reason)
            return datetime.datetime.min

    def urls(self, product: str) -> Iterable[str]:  # pylint: disable=unused-argument
        """ Return the url(s) of the performance report for the specified product and version. """
        return self.__report_urls or [self.url()]

    def __rows(self, url):
        """ Return the rows from the CSV file. """
        data = self.url_read(url, encoding='iso-8859-1')
        return csv.reader(data.split('\n'), delimiter=';')


class SpiritSplunkCSVPerformanceLoadTestReport(SpiritSplunkCSVPerformanceReport):
    """ A Spirit Splunk CSV performance load test. """
    metric_source_name = 'Spirit Splunk CSV performanceloadtestrapport'


class SpiritSplunkCSVPerformanceEnduranceTestReport(SpiritSplunkCSVPerformanceReport):
    """ A Spirit Splunk CSV performance endurance test. """
    metric_source_name = 'Spirit Splunk CSV performanceduurtestrapport'


class SpiritSplunkCSVPerformanceScalabilityTestReport(SpiritSplunkCSVPerformanceReport):
    """ A Spirit Splunk CSV performance scalability test. """
    metric_source_name = 'Spirit Splunk CSV performanceschaalbaarheidstestrapport'
