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


import functools
import logging
import traceback

import bs4

from . import url_opener
from .. import domain


class ZAPScanReport(domain.MetricSource):
    """ Class representing ZAP Scan reports. """
    metric_source_name = 'ZAP Scan rapport'

    def __init__(self, **kwargs) -> None:
        self._url_opener = url_opener.UrlOpener(**kwargs)
        super().__init__()

    @functools.lru_cache(maxsize=1024)
    def alerts(self, risk_level: str, *report_urls: str) -> int:
        """ Return the number of alerts of the specified risk level. """
        nr_alerts = 0
        for url in report_urls:
            try:
                nr_alerts += self.__parse_alerts(self.__get_soup(url), risk_level)
            except url_opener.UrlOpener.url_open_exceptions:
                return -1
            except IndexError as reason:
                logging.warning("Couldn't parse alerts with %s risk level from %s: %s", risk_level, url, reason)
                traceback.print_exc()
                return -1
        return nr_alerts

    def get_warnings_info(self, risk_level: str, *report_urls: str) -> list:
        """ Returns the information about the warnings from zap scan report of a certain risk level."""
        warnings = []
        for url in report_urls:
            try:
                warnings += self.__parse_warnings(self.__get_soup(url), risk_level)
            except url_opener.UrlOpener.url_open_exceptions:
                return []
            except IndexError as reason:
                logging.warning("Couldn't parse alert details with %s risk level from %s: %s", risk_level, url, reason)
                traceback.print_exc()
                return []
        return warnings

    @staticmethod
    def __parse_warnings(soup, risk_level: str) -> list:
        warnings = []
        headers = soup.find_all('tr', attrs={"class": "risk-{level}".format(level=risk_level)})
        for header in headers:
            name = header.find_all('th')[1].string
            description = header.find_next_sibling().find_all('td')[1]
            while description.string is None:
                description = description.contents[0]
            warnings.append((name, description.string))
        if not warnings:
            logging.warning("Couldn't find any entries with %s risk level.", risk_level)
        return warnings

    @functools.lru_cache(maxsize=1024)
    def __get_soup(self, url: str):
        """ Return the HTML soup. """
        return bs4.BeautifulSoup(self._url_opener.url_read(url), "lxml")

    @staticmethod
    def __parse_alerts(soup, risk_level: str) -> int:
        """ Get the number of alerts from the HTML soup. """
        summary_table = soup('table', {"class": "summary"})
        # First try the new table format
        # Find the row where the first td contains the specified risk level and get the number of alerts from
        # the second td.
        if summary_table:
            for row in summary_table[0]('tr'):
                if row('td') and row('td')[0].text == risk_level.capitalize():
                    return int(row('td')[1].text)
            logging.warning("Risk level %s could not be found in ZAP Scan report.", risk_level)
            return -1
        table_list = soup('table')
        # Prevent IndexError in case of empty table
        if table_list:
            summary_table = table_list[0]
            # Find the row where the first td contains the specified risk level and get the number of alerts from
            # the second td. We use item(text=True)[0] to skip font and anchor tags and get the inner text node.
            alert = [row('td')[1](text=True)[0] for row in summary_table('tr')
                     if row('td')[0](text=True)[0] == risk_level.capitalize()][0]
            return int(alert)
        logging.warning("Summary table could not be found in ZAP Scan report.")
        return -1
