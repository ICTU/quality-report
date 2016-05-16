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

import datetime
import unittest

import BeautifulSoup

from qualitylib.metric_source import Birt
from qualitylib.metric_source.birt import SprintProgressReport


TEST_DESIGN_HTML = """
    <table id="__bookmark_1">
        <tr>
            <th><div>Application</div></th>
            <th><div>Nr. of userstories</div></th>
            <th><div>Nr. of userstories with LTC's</div></th>
            <th><div>Nr. of userstories with too few LTC's</div></th>
        </tr>
        <tr>
            <td><div>bulk</div></td>
            <td><div>20</div></td>
            <td><div>14</div></td>
            <td><div>6</div></td>
        </tr>
    </table>
    <table id="__bookmark_2">
        <tr>
            <th><div>Application</div></th>
            <th><div>Nr. of userstories</div></th>
            <th><div>Reviewed userstories</div></th>
            <th><div>Approved userstories</div></th>
            <th><div>Not approved userstories</div></th>
            <th><div>Nr. of finished userstories</div></th>
            <th><div>Nr. of LTC's</div></th>
            <th><div>Reviewed LTC's</div></th>
            <th><div>Approved LTC's</div></th>
            <th><div>Not approved LTC's</div></th>
        </tr>
        <tr>
            <td><div>bulk</div></td>
            <td><div>10</div></td>
            <td><div>9</div></td>
            <td><div>8</div></td>
            <td><div>1</div></td>
            <td><div>7</div></td>
            <td><div>6</div></td>
            <td><div>5</div></td>
            <td><div>4</div></td>
            <td><div>1</div></td>
        </tr>
    </table>
    <table id="__bookmark_3">
        <tr>
            <th><div>Application</div></th>
            <th><div>Nr. of LTCs</div></th>
            <th><div>Nr. of LTC's that should be implemented</div></th>
            <th><div>Implemented</div></th>
            <th><div>Not implemented</div></th>
            <th><div>Nr. of missing implementations</div></th>
            <th><div>Unneeded implementations</div></th>
            <th><div>Nr. of manual LTC's</div></th>
            <th><div>Nr. of untested manual LTC's</div></th>
        </tr>
        <tr>
            <td><div>bulk</div></td>
            <td><div>6</div></td>
            <td><div>6</div></td>
            <td><div>4</div></td>
            <td><div>2</div></td>
            <td><div>3</div></td>
            <td><div>0</div></td>
            <td><div>5</div></td>
            <td><div>0</div></td>
        </tr>
    </table>
"""

SPRINT_PROGRESS_REPORT_HTML = """
<table>
    <table>
        <table>
            <tr>
                <td><div>Gerealiseerde punten in sprint:</div></td>
                <td><div>20</div></td>
            </tr>
            <tr>
                <td><div>Geplande punten in sprint:</div></td>
                <td><div>23,5</div></td>
            </tr>
            <tr>
                <td><div>Startdatum sprint:</div></td>
                <td><div>01-02-2013</div></td>
            </tr>
            <tr>
                <td><div>Einddatum sprint:</div></td>
                <td><div>21-02-2013</div></td>
            </tr>
            <tr>
                <td><div>Vandaag is dag:</div></td>
                <td><div>14</div></td>
            </tr>
            <tr>
                <td><div>Prognose sprint:</div></td>
                <td><div>21</div></td>
            </tr>
        </table>
    </table>
</table>
"""

SPRINT_PROGRESS_REPORT_HTML_MISSING_DATA = """
<table>
    <table>
        <table>
            <tr>
                <td><div>Gerealiseerde punten in sprint:</div></td>
                <td><div></div></td>
            </tr>
            <tr>
                <td><div>Geplande punten in sprint:</div></td>
                <td><div>23,5</div></td>
            </tr>
            <tr>
                <td><div>Startdatum sprint:</div></td>
                <td><div>01-02-2013</div></td>
            </tr>
            <tr>
                <td><div>Einddatum sprint:</div></td>
                <td><div></div></td>
            </tr>
            <tr>
                <td><div>Vandaag is dag:</div></td>
                <td><div>14</div></td>
            </tr>
            <tr>
                <td><div>Prognose sprint:</div></td>
                <td><div>21</div></td>
            </tr>
        </table>
    </table>
</table>
"""

MANUAL_TEST_EXECUTION_HTML_NEVER_EXECUTED = """
<table>
    <tr>
        <td>
            <table id="__bookmark_1">
                <tr>
                    <th></th>
                    <th><div>Aanmaakdatum</div></th>
                    <th><div>Laatst geslaagd</div></th>
                    <th><div>Tester</div></th>
                </tr>
                <tr>
                    <td><div>BMGUI-102</div></td>
                    <td><div>2013-01-01</div></td>
                    <td><div><div>&#xa0;</div></div></td>
                    <td><div><div>&#xa0;</div></div></td>
                </tr>
                <tr>
                    <td><div>BMGUI-103</div></td>
                    <td><div><div>&3xa0;</div></div></td>
                    <td><div><div>&#xa0;</div></div></td>
                    <td><div><div>&#xa0;</div></div></td>
                </tr>
                <tr>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                </tr>
                <tr>
                    <td><div>BMGUI-35</div></td>
                    <td><div>2013-04-01</div></td>
                    <td><div>2013-04-04</div></td>
                    <td><div>Tjarda</div></td>
                </tr>
            </table>
        </td>
    </tr>
</table>
"""

MANUAL_TEST_EXECUTION_HTML = """
<table>
    <tr>
        <td>
            <table>
                <tr>
                    <th></th>
                    <th><div>Aanmaakdatum</div></th>
                    <th><div>Laatst geslaagd</div></th>
                    <th><div>Tester</div></th>
                </tr>
                <tr>
                    <td><div>BGUI-100</div></td>
                    <td><div>2013-03-01</div></td>
                    <td><div>2013-03-19</div></td>
                    <td><div class="style_7">Tjarda</div></td>
                </tr>
                <tr valign="top">
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                </tr>
                <tr>
                    <td><div>BGUI-125</div></td>
                    <td><div>2013-03-01</div></td>
                    <td><div>2013-03-19</div></td>
                    <td><div>Tjarda</div></td>
                </tr>
            </table>
        </td>
    </tr>
</table>
"""


class BirtUnderTest(Birt):  # pylint: disable=too-few-public-methods
    """ Override the soup method to return a fixed HTML fragment. """
    html = ''

    def soup(self, url):  # pylint: disable=unused-argument
        """ Return the static html. """
        return BeautifulSoup.BeautifulSoup(self.html)


class BirtTest(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """ Unit tests for the Birt class. """

    def setUp(self):
        self.__birt = BirtUnderTest('http://birt/')

    def test_url(self):
        """ Test the url. """
        self.assertEqual('http://birt/birt/', self.__birt.url())

    def test_test_design_url(self):
        """ Test the test design url. """
        self.assertEqual('http://birt/birt/preview?__report=report/test_design.rptdesign',
                         self.__birt.test_design_url())

    def test_whats_missing_url(self):
        """ Test the what's missing report url. """
        self.assertEqual('http://birt/birt/preview?__report=report/whats_missing.rptdesign&application=product',
                         self.__birt.whats_missing_url('product'))

    def test_manual_test_url_trunk(self):
        """ Test the manual test execution url for the trunk. """
        self.assertEqual('http://birt/birt/preview?__report=report/manual_test_execution_report.rptdesign&'
                         'application=product&version=trunk',
                         self.__birt.manual_test_execution_url('product'))

    def test_manual_test_url_version(self):
        """ Test the manual test execution url with a specific version. """
        self.assertEqual('http://birt/birt/preview?__report=report/manual_test_execution_report.rptdesign&'
                         'application=product&version=1',
                         self.__birt.manual_test_execution_url('product', '1'))

    def test_sprint_progress_url(self):
        """ Test the sprint progress url. """
        self.assertEqual('http://birt/birt/preview?__report=report/sprint_voortgang.rptdesign&project=team',
                         self.__birt.sprint_progress_url('team'))

    def test_has_no_test_design(self):
        """ Test checking for test design information with a product that has no test design information in Birt
            (i.e. user stories, logical test cases, etc.). """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertFalse(self.__birt.has_test_design('product does not exist'))

    def test_non_existing_product(self):
        """ Test that metrics for non-existing products return -1. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(-1, self.__birt.nr_ltcs('product does not exist'))

    def test_has_test_design(self):
        """ Test checking for test design information with a product that has test design information in Birt
            (i.e. user stories, logical test cases, etc.).  """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertTrue(self.__birt.has_test_design('bulk'))

    def test_nr_user_stories_with_sufficient_ltcs(self):
        """ Test that the number of user stories with sufficient number of logical test cases is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(4, self.__birt.nr_user_stories_with_sufficient_ltcs('bulk'))

    def test_nr_automated_ltcs(self):
        """ Test the number of automated logical test cases is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(3, self.__birt.nr_automated_ltcs('bulk'))

    def test_nr_user_stories(self):
        """ Test that the number of user stories is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(10, self.__birt.nr_user_stories('bulk'))

    def test_reviewed_user_stories(self):
        """ Test that the number of reviewed user stories is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(9, self.__birt.reviewed_user_stories('bulk'))

    def test_approved_user_stories(self):
        """ Test that the number of approved user stories is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(8, self.__birt.approved_user_stories('bulk'))

    def test_not_approved_user_stories(self):
        """ Test that the number of not approved user stories is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(1, self.__birt.not_approved_user_stories('bulk'))

    def test_nr_ltcs(self):
        """ Test that the number of logical test cases is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(6, self.__birt.nr_ltcs('bulk'))

    def test_reviewed_ltcs(self):
        """ Test that the number of reviewed logical test cases is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(5, self.__birt.reviewed_ltcs('bulk'))

    def test_approved_ltcs(self):
        """ Test that the number of approved logical test cases is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(4, self.__birt.approved_ltcs('bulk'))

    def test_not_approved_ltcs(self):
        """ Test that the number of not approved logical test cases is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(1, self.__birt.not_approved_ltcs('bulk'))

    def test_nr_ltcs_to_be_automated(self):
        """ Test that the number of logical test cases to be automated is correct. """
        self.__birt.html = TEST_DESIGN_HTML
        self.assertEqual(6, self.__birt.nr_ltcs_to_be_automated('bulk'))

    def test_nr_manual_ltcs(self):
        """ Test that the number of manual logical test cases is correct. """
        self.__birt.html = MANUAL_TEST_EXECUTION_HTML
        self.assertEqual(2, self.__birt.nr_manual_ltcs('bulk'))

    def test_nr_manual_ltcs_too_old(self):
        """ Test that the number of manual logical test cases that have not been tested recently is correct. """
        self.__birt.html = MANUAL_TEST_EXECUTION_HTML
        self.assertEqual(2, self.__birt.nr_manual_ltcs_too_old('bulk', 'trunk', 14))

    def test_no_date_manual_tests(self):
        """ Test that the date of the last manual test execution is correct. """
        self.__birt.html = MANUAL_TEST_EXECUTION_HTML_NEVER_EXECUTED
        date = self.__birt.date_of_last_manual_test('bulk')
        self.assertEqual(datetime.datetime(1, 1, 1), date)

    def test_late_date_manual_tests(self):
        """ Test that the date of the last manual test execution is correct. """
        self.__birt.html = MANUAL_TEST_EXECUTION_HTML
        date = self.__birt.date_of_last_manual_test('bulk')
        self.assertEqual(datetime.datetime(2013, 3, 19), date)


class BirtSprintProgressReportUnderTest(SprintProgressReport):  # pylint: disable=too-few-public-methods
    """ Override the soup method to return a fixed HTML fragment. """
    html = ''

    def soup(self, url):  # pylint: disable=unused-argument
        """ Return the static html. """
        return BeautifulSoup.BeautifulSoup(self.html)


class BirtSprintProgressReportTest(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """ Unit tests for the Birt sprint progress report. """

    def setUp(self):
        self.__birt = BirtSprintProgressReportUnderTest('http://birt/%s')
        self.__birt.html = SPRINT_PROGRESS_REPORT_HTML

    def test_actual_velocity(self):
        """ Test that the actual velocity is the number of points realized per day so far. """
        self.assertEqual(20 / 14., self.__birt.actual_velocity('birt_id'))

    def test_planned_velocity(self):
        """ Test that the planned velocity is correct. """
        self.assertEqual(23.5 / 15, self.__birt.planned_velocity('birt_id'))

    def test_required_velocity(self):
        """ Test that the required velocity is correct. """
        self.assertEqual(3.5 / 2, self.__birt.required_velocity('birt_id'))

    def test_days_in_sprint_no_end_date(self):
        """ Test that the days in the sprint is zero when the end date is unknown. """
        self.__birt.html = SPRINT_PROGRESS_REPORT_HTML_MISSING_DATA
        self.assertEqual(0, self.__birt.days_in_sprint('birt_id'))

    def test_missing_velocity(self):
        """ Test that the actual velocity is zero when the data is missing. """
        self.__birt.html = SPRINT_PROGRESS_REPORT_HTML_MISSING_DATA
        self.assertEqual(0., self.__birt.actual_velocity('birt_id'))
