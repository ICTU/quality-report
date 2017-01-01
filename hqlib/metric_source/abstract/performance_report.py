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

import datetime

from .. import beautifulsoup
from ..url_opener import UrlOpener
from ... import domain, utils


class PerformanceReport(domain.MetricSource, beautifulsoup.BeautifulSoupOpener):
    """ Abstract class representing a performance report. """
    metric_source_name = 'Performancerapport'
    needs_metric_source_id = True
    COLUMN_90_PERC = 0  # Subclass responsibility

    def __init__(self, report_url, *args, **kwargs):
        super(PerformanceReport, self).__init__(url=report_url, *args, **kwargs)

    def urls(self, product):
        """ Return the report urls for the specified product. """
        raise NotImplementedError  # pragma: no cover

    def queries(self, product):
        """ Return the number of performance queries. """
        try:
            return len(self._query_rows(product))
        except UrlOpener.url_open_exceptions:
            return -1

    def queries_violating_max_responsetime(self, product):
        """ Return the number of performance queries that violate the maximum response time. """
        try:
            return self.__queries_violating_response_time(product, 'red')
        except UrlOpener.url_open_exceptions:
            return -1

    def queries_violating_wished_responsetime(self, product):
        """ Return the number of performance queries that violate the maximum response time we'd like to meet. """
        try:
            return self.__queries_violating_response_time(product, 'yellow')
        except UrlOpener.url_open_exceptions:
            return -1

    @utils.memoized
    def date(self, product):
        """ Return the date when performance was last measured. """
        urls = self.urls(product)
        if urls:
            url = list(urls)[0]  # Any url is fine
            try:
                soup = self.soup(url)
            except UrlOpener.url_open_exceptions:
                return datetime.datetime.min
            return self._date_from_soup(soup)
        else:
            return datetime.datetime.min

    def _query_rows(self, product):
        """ Return the queries for the specified product. """
        raise NotImplementedError  # pragma: no cover

    def __queries_violating_response_time(self, product, color):
        """ Return the number of queries that are violating either the maximum or the desired response time. """
        return len([row for row in self._query_rows(product)
                    if color in row('td')[self.COLUMN_90_PERC]['class']])

    def _date_from_soup(self, soup):
        """ Return the date when the performance was last measured based on the report at the url. """
        raise NotImplementedError  # pragma: no cover


class PerformanceLoadTestReport(PerformanceReport):
    """ Performance load test report. """
    def urls(self, product):
        """ Return the report urls for the specified product. """
        raise NotImplementedError  # pragma: no cover

    def _query_rows(self, product):
        """ Return the queries for the specified product. """
        raise NotImplementedError  # pragma: no cover

    def _date_from_soup(self, soup):
        """ Return the date when the performance was last measured based on the report at the url. """
        raise NotImplementedError  # pragma: no cover


class PerformanceEnduranceTestReport(PerformanceReport):
    """ Performance endurance test report. """
    def urls(self, product):
        """ Return the report urls for the specified product. """
        raise NotImplementedError  # pragma: no cover

    def _query_rows(self, product):
        """ Return the queries for the specified product. """
        raise NotImplementedError  # pragma: no cover

    def _date_from_soup(self, soup):
        """ Return the date when the performance was last measured based on the report at the url. """
        raise NotImplementedError  # pragma: no cover


class PerformanceScalabilityTestReport(PerformanceReport):
    """ Performance scalability test report. """
    def urls(self, product):
        """ Return the report urls for the specified product. """
        raise NotImplementedError  # pragma: no cover

    def _query_rows(self, product):
        """ Return the queries for the specified product. """
        raise NotImplementedError  # pragma: no cover

    def _date_from_soup(self, soup):
        """ Return the date when the performance was last measured based on the report at the url. """
        raise NotImplementedError  # pragma: no cover
