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
import logging
from typing import List

from hqlib.typing import DateTime
from . import beautifulsoup, url_opener
from .. import utils, domain


class Birt(domain.MetricSource, beautifulsoup.BeautifulSoupOpener):
    """ Class representing the Birt report engine instance. """

    metric_source_name = 'Birt reports'

    def __init__(self, birt_url: str) -> None:
        birt_url += 'birt/'
        super().__init__(url=birt_url)
        birt_report_url = birt_url + 'preview?__report=reports/'
        self.__test_design_url = birt_report_url + 'test_design.rptdesign'
        self.__manual_test_execution_url = birt_report_url + \
            'manual_test_execution_report.rptdesign&version={ver}'
        self.__whats_missing_url = birt_report_url + 'whats_missing.rptdesign'

    def __getattr__(self, attribute):  # pragma: no cover
        # Forward method calls that this class doesn't support to the sprint progress report.
        return getattr(self.__sprint_progress_report, attribute)

    # Urls to reports

    def test_design_url(self) -> str:
        """ Return the url for the Birt test design report. """
        return self.__test_design_url

    def manual_test_execution_url(self, version: str = 'trunk') -> str:
        """ Return the url for the Birt manual test execution report. """
        return self.__manual_test_execution_url.format(ver=version)

    def whats_missing_url(self) -> str:
        """ Return the What's missing report url for the product. """
        return self.__whats_missing_url

    # Metrics calculated from other metrics:

    def nr_user_stories_with_sufficient_ltcs(self) -> int:
        """ Return the number of user stories that have a sufficient number of logical test cases."""
        nr_user_stories = self.nr_user_stories()
        if nr_user_stories == -1:
            return -1
        return int(nr_user_stories) - int(self.__nr_user_stories_with_too_few_ltcs())

    def nr_automated_ltcs(self) -> int:
        """ Return the number of logical test cases that have been implemented as automated tests. """
        nr_ltcs_to_be_automated = self.nr_ltcs_to_be_automated()
        if nr_ltcs_to_be_automated == -1:
            return -1
        return int(nr_ltcs_to_be_automated) - int(self.__nr_missing_automated_ltcs())

    # Metrics available directly in Birt:

    def nr_user_stories(self) -> int:
        """ Return the number of user stories . """
        return self.__test_design_metric(row_nr=0)

    def __nr_user_stories_with_too_few_ltcs(self) -> int:
        """ Return the number of user stories that have not enough logical test cases associated with them. """
        return self.__test_design_metric(row_nr=2)

    def reviewed_user_stories(self) -> int:
        """ Return the number of reviewed user stories. """
        return self.__test_design_metric(row_nr=3)

    def approved_user_stories(self) -> int:
        """ Return the number of approved user stories. """
        return self.__test_design_metric(row_nr=4)

    def not_approved_user_stories(self) -> int:
        """ Return the number of not approved user stories. """
        return self.__test_design_metric(row_nr=5)

    def nr_ltcs(self) -> int:
        """ Return the number of logical test cases. """
        return self.__test_design_metric(row_nr=6)

    def reviewed_ltcs(self) -> int:
        """ Return the number of reviewed logical test cases for the product. """
        return self.__test_design_metric(row_nr=7)

    def approved_ltcs(self) -> int:
        """ Return the number of approved logical test casess. """
        return self.__test_design_metric(row_nr=8)

    def not_approved_ltcs(self) -> int:
        """ Return the number of disapproved logical test cases. """
        return self.__test_design_metric(row_nr=9)

    def nr_ltcs_to_be_automated(self) -> int:
        """ Return the number of logical test cases for the product that have to be automated. """
        return self.__test_design_metric(row_nr=10)

    def nr_manual_ltcs(self, version: str = 'trunk') -> int:
        """ Return the number of logical test cases for the product that are executed manually. """
        try:
            test_dates = self.__manual_test_dates(version)
        except url_opener.UrlOpener.url_open_exceptions:
            return -1
        return len(test_dates)

    def nr_manual_ltcs_too_old(self, version: str, target: int) -> int:
        """ Return the number of manual logical test cases that have not been executed for target amount of days. """
        try:
            test_dates = self.__manual_test_dates(version)
        except url_opener.UrlOpener.url_open_exceptions:
            return -1
        now = datetime.datetime.now()
        too_old = [date for date in test_dates if (now - date).days > target]
        return len(too_old)

    def __nr_missing_automated_ltcs(self) -> int:
        """ Return the number of logical test cases for the product that should be automated but have not. """
        return self.__test_design_metric(row_nr=13)

    def date_of_last_manual_test(self, version: str = 'trunk') -> DateTime:
        """ Return the date when the product/version was last tested manually. """
        try:
            test_dates = self.__manual_test_dates(version)
        except url_opener.UrlOpener.url_open_exceptions:
            return datetime.datetime.min
        test_dates = test_dates[:]
        # Add today's date so that we report today if there are no manual test cases at all.
        test_dates.append(datetime.datetime.now())
        return min(test_dates)

    def __manual_test_dates(self, version: str) -> List[DateTime]:
        """ Return the manual test cases. """
        url = self.__manual_test_execution_url.format(ver=version)
        try:
            soup = self.soup(url)
        except url_opener.UrlOpener.url_open_exceptions as reason:
            logging.warning("Could not open manual test dates report at %s: %s", url, reason)
            raise
        inner_table = soup('table', {'id': '__bookmark_1'})[0]
        rows = inner_table('tr')[1:]  # Skip header row
        test_dates = []
        for row in rows:
            try:
                row('td')[0]('div')[0]  # Check there's a div in the first column.
            except IndexError:
                continue  # Skip empty row
            last_test_date_string = row('td')[2]('div')[0].string
            try:
                last_test_date = utils.parse_iso_date(last_test_date_string)
            except (TypeError, ValueError):
                # No valid date. Test was never executed. Use test creation date:
                test_creation_date_string = row('td')[1]('div')[0].string
                last_test_date = utils.parse_iso_date(test_creation_date_string)
            test_dates.append(last_test_date)
        return test_dates

    def __test_design_metric(self, row_nr: int) -> int:
        """ Get a metric from a specific row in the test design report."""
        try:
            test_design_report = self.soup(self.__test_design_url)
        except url_opener.UrlOpener.url_open_exceptions as reason:
            logging.warning("Could not open %s: %s", self.__test_design_url, reason)
            return -1
        try:
            return int(test_design_report('div', {'class': 'style_4'})[row_nr].string.replace(',', ''))
        except (ValueError, IndexError) as reason:
            logging.error("Could not obtain row %s from Birt report %s: %s", row_nr, self.__test_design_url, reason)
            return -1
