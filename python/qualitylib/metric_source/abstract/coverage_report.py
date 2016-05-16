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
from __future__ import absolute_import

import datetime
import urllib2

from BeautifulSoup import BeautifulSoup

from .. import url_opener
from ... import utils, domain


class CoverageReport(domain.MetricSource):
    """ Abstract class representing a coverage report. """
    metric_source_name = 'Coverage report'
    needs_metric_source_id = True

    def __init__(self, url_open=None, **kwargs):
        self.__url_open = url_open or url_opener.UrlOpener(**kwargs).url_open
        super(CoverageReport, self).__init__()

    @utils.memoized
    def statement_coverage(self, coverage_url):
        """ Return the ART statement coverage for a specific product. """
        try:
            soup = self.__get_report_soup(coverage_url)
        except urllib2.HTTPError:
            coverage = -1
        else:
            coverage = self._parse_statement_coverage_percentage(soup)
        return coverage

    def _parse_statement_coverage_percentage(self, soup):
        """ Parse the coverage percentage from the soup. """
        raise NotImplementedError  # pragma: no cover

    @utils.memoized
    def branch_coverage(self, coverage_url):
        """ Return the ART branch coverage for a specific product. """
        try:
            soup = self.__get_report_soup(coverage_url)
        except urllib2.HTTPError:
            coverage = -1
        else:
            coverage = self._parse_branch_coverage_percentage(soup)
        return coverage

    def _parse_branch_coverage_percentage(self, soup):
        """ Parse the coverage percentage from the soup. """
        raise NotImplementedError  # pragma: no cover

    @utils.memoized
    def coverage_date(self, coverage_url, now=datetime.datetime.now):
        """ Return the date when the ART coverage for a specific product was last successfully measured. """
        coverage_date_url = self._get_coverage_date_url(coverage_url)
        try:
            soup = BeautifulSoup(self.__url_open(coverage_date_url))
        except urllib2.HTTPError:
            coverage_date = now()
        else:
            coverage_date = self._parse_coverage_date(soup)
        return coverage_date

    def _parse_coverage_date(self, soup):
        """ Parse the coverage date from the soup. """
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    def _get_coverage_date_url(coverage_url):
        """ Return the url for the date when the coverage of the product was last measured. """
        return coverage_url

    @utils.memoized
    def __get_report_soup(self, coverage_url):
        """ Get a beautiful soup of the coverage report. """
        return BeautifulSoup(self.__url_open(coverage_url))
