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
from __future__ import absolute_import

import logging

import bs4

from . import url_opener
from .. import domain


class ZAPScanReport(domain.MetricSource):
    """ Class representing ZAP Scan reports. """
    metric_source_name = 'ZAP Scan rapport'
    needs_metric_source_id = True

    def __init__(self, url_open=None, **kwargs):
        self._url_open = url_open or url_opener.UrlOpener(**kwargs).url_open
        super(ZAPScanReport, self).__init__()

    def alerts(self, risk_level, *report_urls):
        """ Return the number of alerts of the specified risk level. """
        assert risk_level in ('low', 'medium', 'high')
        nr_alerts = 0
        for url in report_urls:
            try:
                soup = bs4.BeautifulSoup(self._url_open(url), "html.parser")
            except url_opener.UrlOpener.url_open_exceptions:
                return -1
            try:
                nr_alerts += self.__parse_alerts(soup, risk_level)
            except IndexError as reason:
                logging.warning("Couldn't parse alerts with %s risk level from %s: %s", risk_level, url, reason)
                return -1
        return nr_alerts

    @staticmethod
    def __parse_alerts(soup, risk_level):
        """ Get the number of alerts from the HTML soup. """
        summary_table = soup('table')[0]
        # Find the row where the first td contains the specified risk level and get the number of alerts form
        # the second td. We use item(text=True)[0] to skip font and anchor tags and get the inner text node.
        alert = [row('td')[1](text=True)[0] for row in summary_table('tr')
                 if row('td')[0](text=True)[0] == risk_level.capitalize()][0]
        return int(alert)
