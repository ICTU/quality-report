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
import logging

from . import beautifulsoup
from .. import utils, domain


class BirtReport(beautifulsoup.BeautifulSoupOpener):
    """ Class representing a specific Birt report. """
    def __init__(self, url):
        super(BirtReport, self).__init__()
        self.__url = url

    def url(self):
        """ Return the url of the report. """
        return self.__url


class SprintProgressReport(BirtReport):
    """ Class representing the sprint progress Birt report. """

    def url(self, team):
        return super(SprintProgressReport, self).url().format(proj=team)

    def actual_velocity(self, team):
        """ Return the actual velocity (in points per day) of the team in the current sprint. """
        current_day = max(1, self.day_in_sprint(team))
        return self.nr_points_realized(team) / float(current_day)

    def planned_velocity(self, team):
        """ Return the planned velocity (in points per day) of the team in the current sprint. """
        sprint_length = max(1, self.days_in_sprint(team))
        return self.nr_points_planned(team) / float(sprint_length)

    def required_velocity(self, team):
        """ Return the required velocity (in points per day) of the team in the current sprint. """
        points_to_do = self.__nr_points_to_do(team)
        days_left = max(1, self.__days_left(team))
        return points_to_do / float(days_left)

    def nr_points_realized(self, team):
        """ Return the number of points realized in the current sprint of the specified team. """
        return self.__parse_float(self.__summary_table_cell(team, 0, 1))

    def nr_points_planned(self, team):
        """ Return the sprint commitment of the team for the current sprint. """
        return self.__parse_float(self.__summary_table_cell(team, 1, 1))

    def days_in_sprint(self, team):
        """ Return the number of days in the current sprint. """
        start_date = self.__sprint_start_date(team)
        end_date = self.__sprint_end_date(team)
        if start_date and end_date:
            return utils.workdays_in_period(start_date, end_date)
        else:
            return 0

    def day_in_sprint(self, team):
        """ Return the number of the current day in the sprint. """
        return self.__parse_float(self.__summary_table_cell(team, 4, 1))

    def __days_left(self, team):
        """ Return the number of days left in the current sprint of the team. """
        return 1 + self.days_in_sprint(team) - self.day_in_sprint(team)

    def __nr_points_to_do(self, team):
        """ Return the number of points to be realized in the current sprint of the specified team. """
        return max(0, self.nr_points_planned(team) - self.nr_points_realized(team))

    def __sprint_start_date(self, team):
        """ Return the start date of the current sprint of the team. """
        return self.__parse_date(self.__summary_table_cell(team, 2, 1))

    def __sprint_end_date(self, team):
        """ Return the end date of the current sprint of the team. """
        return self.__parse_date(self.__summary_table_cell(team, 3, 1))

    @utils.memoized
    def __summary_table_cell(self, team, row_index, column_index):
        """ Return a specific cell from the sprint progress table in the sprint progress Birt report. """
        summary_table = self.__summary_table(team)
        row = summary_table('tr')[row_index]
        cell = row('td')[column_index]
        return cell('div')[0].string

    @utils.memoized
    def __summary_table(self, team):
        """ Return the sprint progress table in the sprint progress Birt report. """
        soup = self.soup(self.url(team))
        return soup('table')[0]('table')[0]('table')[0]

    @staticmethod
    def __parse_date(date_string):
        """ Parse the date string and return a date object. """
        try:
            day, month, year = date_string.split('-')
        except AttributeError:
            return None
        return datetime.date(int(year), int(month), int(day))

    @staticmethod
    def __parse_float(float_string):
        """ Parse the float string and return the float. """
        if float_string:
            float_string = float_string.replace(',', '.')
        try:
            return float(float_string)
        except (ValueError, TypeError):
            return 0.


class Birt(domain.MetricSource, beautifulsoup.BeautifulSoupOpener):
    """ Class representing the Birt report engine instance. """

    metric_source_name = 'Birt reports'
    needs_metric_source_id = True

    def __init__(self, birt_url):
        birt_url += 'birt/'
        super(Birt, self).__init__(url=birt_url)
        birt_report_url = birt_url + 'preview?__report=report/'
        self.__test_design_url = birt_report_url + 'test_design.rptdesign'
        self.__manual_test_execution_url = birt_report_url + \
            'manual_test_execution_report.rptdesign&application={app}&version={ver}'
        self.__whats_missing_url = birt_report_url + 'whats_missing.rptdesign&application={app}'
        sprint_progress_url = birt_report_url + 'sprint_voortgang.rptdesign&project={proj}'
        self.__sprint_progress_report = SprintProgressReport(sprint_progress_url)
        self.__test_design_report = None
        self.__manual_test_report = None

    def __getattr__(self, attribute):  # pragma: no cover
        # Forward method calls that this class doesn't support to the sprint progress report.
        return getattr(self.__sprint_progress_report, attribute)

    # Urls to reports

    def test_design_url(self):
        """ Return the url for the Birt test design report. """
        return self.__test_design_url

    def manual_test_execution_url(self, product, version='trunk'):
        """ Return the url for the Birt manual test execution report. """
        return self.__manual_test_execution_url.format(app=product, ver=version)

    def sprint_progress_url(self, team):
        """ Return the url for the Birt sprint progress report. """
        return self.__sprint_progress_report.url(team)

    def whats_missing_url(self, product):
        """ Return the What's missing report url for the product. """
        return self.__whats_missing_url.format(app=product)

    # Misc

    @utils.memoized
    def has_test_design(self, product):
        """ Return whether the product has a test design (i.e. user stories, logical test cases, reviews of
            user stories and logical test cases, etc.) """
        soup = self.soup(self.__test_design_url)
        user_story_table = soup('table', id='__bookmark_1')[0]
        for row in user_story_table('tr')[1:]:  # Skip header
            product_name = row('td')[0]('div')[0].string
            if product_name == product:
                return True
        return False

    # Metrics calculated from other metrics:

    def nr_user_stories_with_sufficient_ltcs(self, product):
        """ Return the number of user stories that have a sufficient number of logical test cases."""
        return int(self.nr_user_stories(product)) - int(self.__nr_user_stories_with_too_few_ltcs(product))

    def nr_automated_ltcs(self, product):
        """ Return the number of logical test cases that have been implemented as automated tests. """
        return int(self.nr_ltcs_to_be_automated(product)) - int(self.__nr_missing_automated_ltcs(product))

    # Metrics available directly in Birt:

    def __nr_user_stories_with_too_few_ltcs(self, product):
        """ Return the number of user stories that have not enough logical test cases associated with them. """
        return self.__test_design_metric(product, table_nr=1, column_nr=3)

    def nr_user_stories(self, product):
        """ Return the number of user stories for the product. """
        return self.__test_design_metric(product, table_nr=2, column_nr=1)

    def reviewed_user_stories(self, product):
        """ Return the number of reviewed user stories for the product. """
        return self.__test_design_metric(product, table_nr=2, column_nr=2)

    def approved_user_stories(self, product):
        """ Return the number of approved user stories for the product. """
        return self.__test_design_metric(product, table_nr=2, column_nr=3)

    def not_approved_user_stories(self, product):
        """ Return the number of not approved user stories for the product. """
        return self.__test_design_metric(product, table_nr=2, column_nr=4)

    def nr_ltcs(self, product):
        """ Return the number of logical test cases for the product. """
        return self.__test_design_metric(product, table_nr=2, column_nr=6)

    def reviewed_ltcs(self, product):
        """ Return the number of reviewed logical test cases for the product. """
        return self.__test_design_metric(product, table_nr=2, column_nr=7)

    def approved_ltcs(self, product):
        """ Return the number of approved logical test cases for the product. """
        return self.__test_design_metric(product, table_nr=2, column_nr=8)

    def not_approved_ltcs(self, product):
        """ Return the number of not approved logical test cases for the product. """
        return self.__test_design_metric(product, table_nr=2, column_nr=9)

    def nr_ltcs_to_be_automated(self, product):
        """ Return the number of logical test cases for the product that have to be automated. """
        return self.__test_design_metric(product, table_nr=3, column_nr=2)

    def nr_manual_ltcs(self, product, version='trunk'):
        """ Return the number of logical test cases for the product that are executed manually. """
        return len(self.__manual_test_dates(product, version))

    def nr_manual_ltcs_too_old(self, product, version, target):
        """ Return the number of manual logical test cases that have not been executed for target amount of days. """
        test_dates = self.__manual_test_dates(product, version)
        now = datetime.datetime.now()
        too_old = [date for date in test_dates if (now - date).days > target]
        return len(too_old)

    def __nr_missing_automated_ltcs(self, product):
        """ Return the number of logical test cases for the product that should be automated but have not. """
        return self.__test_design_metric(product, table_nr=3, column_nr=5)

    @utils.memoized
    def date_of_last_manual_test(self, product, version='trunk'):
        """ Return the date when the product/version was last tested manually. """
        test_dates = self.__manual_test_dates(product, version)[:]
        # Add today's date so that we report today if there are no manual test
        # cases at all.
        test_dates.append(datetime.datetime.now())
        return min(test_dates)

    @utils.memoized
    def __manual_test_dates(self, product, version):
        """ Return the manual test cases. """
        soup = self.soup(self.__manual_test_execution_url.format(app=product, ver=version))
        inner_table = soup('table')[0]('table')[0]
        rows = inner_table('tr')[1:]  # Skip header row
        test_dates = []
        for row in rows:
            try:
                last_test_date_string = row('td')[2]('div')[0].string
                try:
                    last_test_date = utils.parse_iso_date(last_test_date_string)
                except (TypeError, ValueError):
                    # No valid date at all. Test was never executed.
                    last_test_date = datetime.datetime.min
                test_dates.append(last_test_date)
            except IndexError:
                continue  # Skip empty row
        return test_dates

    @utils.memoized
    def __test_design_metric(self, product, table_nr, column_nr):
        """ Get a metric for a specific product from a specific table and column in that table.
            The product determines the row in the table."""

        def table(table_nr):
            """ Return the table with the specified number. """
            return self.__test_design_report('table', id='__bookmark_{nr}'.format(nr=table_nr))[0]

        def rows(table):
            """ Return the rows in the table. """
            return table('tr')[1:]  # Skip header row

        def row_contains_product(row, product):
            """ Return whether the row contains the product. """
            return row('td')[0]('div')[0].string == product

        def cell(row, column_nr):
            """ Return the cell in the specified row and column. """
            return row('td')[column_nr]('div')[0].string

        if not self.__test_design_report:
            self.__test_design_report = self.soup(self.__test_design_url)
        for row in rows(table(table_nr)):
            if row_contains_product(row, product):
                return int(cell(row, column_nr))

        logging.warn("Could not obtain product %s from column# %d of table# %d in Birt report: %s",
                     product, column_nr, table_nr, self.__test_design_url)

        return -1  # Product not found
