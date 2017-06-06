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

import datetime
import functools
import bs4
import logging
import dateutil.parser
from typing import Callable

from . import url_opener
from .. import domain
from hqlib.typing import DateTime


class OpenVASScanReport(domain.MetricSource):
    """ Class representing open VAS Scan reports. """
    metric_source_name = 'Open VAS Scan rapport'
    needs_metric_source_id = True

    def __init__(self, url_open: Callable[[str], str]=None, **kwargs) -> None:
        self._url_open = url_open or url_opener.UrlOpener(**kwargs).url_open
        super().__init__()

    def alerts(self, risk_level: str, *report_urls: str) -> int:
        """ Return the number of alerts of the specified risk level. """
        nr_alerts = 0
        for url in report_urls:
            try:
                soup = self.__get_soup(url)
            except url_opener.UrlOpener.url_open_exceptions:
                return -1
            else:
                try:
                    nr_alerts += self.__parse_alerts(soup, risk_level)
                except IndexError as reason:
                    logging.error("Error parsing alerts from report at %s: %s", url, reason)
                    return -1
        return nr_alerts

    @staticmethod
    def __parse_alerts(soup, risk_level: str) -> int:
        """ Get the number of alerts from the HTML soup. """
        summary_table = soup('table')[0]('table')[1]  # The whole report is one big table with nested tables.
        column = dict(high=3, medium=4, low=5)[risk_level]
        return int(summary_table('tr')[-1]('td')[column].string)

    def datetime(self, *report_urls: str) -> DateTime:
        """ Return the date/time of the reports. """
        try:
            return min([self.__report_datetime(report_url) for report_url in report_urls],
                       default=datetime.datetime.min)
        except IndexError as reason:
            logging.error("Error parsing date from report urls at %s: %s", report_urls, reason)
            return datetime.datetime.min

    def __report_datetime(self, report_url: str) -> DateTime:
        """ Return the date/time of the report. """
        try:
            soup = self.__get_soup(report_url)
        except url_opener.UrlOpener.url_open_exceptions:
            return datetime.datetime.min
        summary_table = soup('table')[0]('table')[0]  # The whole report is one big table with nested tables.
        date_string = summary_table('tr')[1]('td')[1].string
        return dateutil.parser.parse(date_string, ignoretz=True)

    @functools.lru_cache(maxsize=1024)
    def __get_soup(self, url: str):
        """ Get the soup from the url. """
        return bs4.BeautifulSoup(self._url_open(url), "lxml")
