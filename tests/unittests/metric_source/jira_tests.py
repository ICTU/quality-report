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

import io
import unittest
import urllib2

from hqlib.metric_source import Jira


class JiraUnderTest(Jira):  # pylint: disable=too-few-public-methods
    """ Override class to return a fixed JSON file. """

    nr_query_results = 5
    view_url = u'http://view'
    issues = u'[]'

    def url_open(self, url):  # pylint: disable=unused-argument
        """ Return the static content. """
        if 'raise' in url:
            raise urllib2.HTTPError(None, None, None, None, None)
        else:
            return io.StringIO(u'{{"searchUrl": "http://search", "viewUrl": "{0}", "total": {1}, '
                               u'"issues": {2}}}'.format(self.view_url, self.nr_query_results, self.issues))


class JiraTestCase(unittest.TestCase):
    """ Base class for Jira tests. """

    url = 'http://jira/'

    def jira(self, *args, **kwargs):
        """ Factory function for creating Jira instances. """
        return JiraUnderTest(self.url, 'username', 'password', *args, **kwargs)


class JiraTest(JiraTestCase):
    """ Unit tests for the Jira class. """

    def test_url(self):
        """ Test the Jira url. """
        self.assertEqual(self.url, self.jira().url())


class JiraBugTest(JiraTestCase):
    """ Unit tests for the Jira bug queries. """

    def setUp(self):
        self.__jira = self.jira(open_bug_query_id=123, open_security_bug_query_id=456,
                                open_static_security_analysis_bug_query_id=567)

    def test_bugs(self):
        """ Test that the number of open bugs is correct. """
        self.assertEqual(self.__jira.nr_query_results, self.__jira.nr_open_bugs())

    def test_bugs_without_query(self):
        """ Test that the number of open bugs is -1 when Jira has no query id. """
        self.assertEqual(-1, self.jira().nr_open_bugs())

    def test_bugs_url(self):
        """ Test that the url is correct. """
        self.assertEqual(self.__jira.view_url, self.__jira.nr_open_bugs_url())

    def test_security_bugs(self):
        """ Test that the number of open security bugs is correct. """
        self.assertEqual(self.__jira.nr_query_results, self.__jira.nr_open_security_bugs())

    def test_security_bugs_without_query(self):
        """ Test that the number of open security bugs is -1 when Jira has no query id. """
        self.assertEqual(-1, self.jira().nr_open_security_bugs())

    def test_security_bugs_url(self):
        """ Test that the url is correct. """
        self.assertEqual(self.__jira.view_url, self.__jira.nr_open_security_bugs_url())

    def test_static_security_analysis_bugs(self):
        """ Test that the number of open static security analysis bugs is correct. """
        self.assertEqual(self.__jira.nr_query_results, self.__jira.nr_open_static_security_analysis_bugs())

    def test_static_security_analysis_bugs_without_query(self):
        """ Test that the number of open security bugs is -1 when Jira has no query id. """
        self.assertEqual(-1, self.jira().nr_open_static_security_analysis_bugs())

    def test_static_security_analysis_bugs_url(self):
        """ Test that the url is correct. """
        self.assertEqual(self.__jira.view_url, self.__jira.nr_open_static_security_analysis_bugs_url())


class JiraManualTestCasesTest(JiraTestCase):
    """ Unit tests for the Jira manual test cases queries. """

    def setUp(self):
        self.__jira = self.jira(manual_test_cases_query_id=654)

    def test_nr_manual_tests(self):
        """ Test that the correct number of manual test cases is returned. """
        self.assertEqual(5, self.__jira.nr_manual_test_cases())

    def test_nr_manual_tests_without_query(self):
        """ Test that the number of manual tests is -1 when Jira has no query id. """
        self.assertEqual(-1, self.jira().nr_manual_test_cases())

    def test_manual_test_time(self):
        """ Test that the total number of minutes spend on manual test cases is correct. """
        self.__jira.issues = u'[{"fields": {"customfield_11700": "20"}},' \
                             ' {"fields": {"customfield_11700": 100}},' \
                             ' {"fields": {"customfield_11700": null}}]'
        self.assertEqual(120, self.__jira.manual_test_cases_time())

    def test_manual_test_time_without_query(self):
        """ Test that the manual test time is -1 when Jira has no query id. """
        self.assertEqual(-1, self.jira().manual_test_cases_time())

    def test_nr_manual_tests_not_measured(self):
        """ Test that the number of manual test cases not measured is correct. """
        self.__jira.issues = u'[{"fields": {"customfield_11700": "20"}},' \
                             ' {"fields": {"customfield_11700": 100}},' \
                             ' {"fields": {"customfield_11700": null}}]'
        self.assertEqual(1, self.__jira.nr_manual_test_cases_not_measured())

    def test_nr_manual_tests_not_measured_without_query(self):
        """ Test that the number of manual test cases not measured is -1 when Jira has no query id. """
        self.assertEqual(-1, self.jira().nr_manual_test_cases_not_measured())

    def test_manual_test_time_url(self):
        """ Test that the url is correct. """
        self.assertEqual(self.__jira.view_url, self.__jira.manual_test_cases_url())


class JiraReadyUserStoriesTest(JiraTestCase):
    """ Unit tests for the Jira ready user stories query. """

    def setUp(self):
        self.__jira = self.jira(user_stories_ready_query_id=555)

    def test_points_ready(self):
        """ Test that the total number points of ready user stories is correct. """
        self.__jira.issues = u'[{"fields": {"customfield_10002": "1.0"}},' \
                             ' {"fields": {"customfield_10002": "8.0"}},' \
                             ' {"fields": {"customfield_10002": null}}]'
        self.assertEqual(9, self.__jira.nr_story_points_ready())

    def test_points_ready_without_query(self):
        """ Test that the number of points is -1 when Jira has no query id. """
        self.assertEqual(-1, self.jira().nr_story_points_ready())

    def test_user_stories_ready_url(self):
        """ Test that the url is correct. """
        self.assertEqual(self.__jira.view_url, self.__jira.user_stories_ready_url())


class JiraTechnicalDebtTest(JiraTestCase):
    """ Unit tests for the Jira technical debt issues query. """

    def setUp(self):
        self.__jira = self.jira(technical_debt_issues_query_id=444)

    def test_nr_technical_debt_issues(self):
        """ Test that the correct number of technical debt issues is returned. """
        self.assertEqual(5, self.__jira.nr_technical_debt_issues())

    def test_nr_technical_debt_issues_without_query(self):
        """ Test that the number of technical debt issues is -1 when Jira has no query id. """
        self.assertEqual(-1, self.jira().nr_technical_debt_issues())

    def test_technical_debt_issues_url(self):
        """ Test that the url is correct. """
        self.assertEqual(self.__jira.view_url, self.__jira.nr_technical_debt_issues_url())


class JiraUserStoryAssessmentTest(JiraTestCase):
    """ Unit tests for the user stories without assessment queries of Jira. """

    def setUp(self):
        self.__jira = self.jira(user_stories_without_security_risk_query_id=567,
                                user_stories_without_performance_risk_query_id=789)

    def test_security_risk(self):
        """ Test that the correct number of user stories without security risk assessment is returned. """
        self.assertEqual(5, self.__jira.nr_user_stories_without_security_risk_assessment())

    def test_security_risk_without_query(self):
        """ Test that the number of user stories is -1 when Jira hasn't got the right query. """
        self.assertEqual(-1, self.jira().nr_user_stories_without_security_risk_assessment())

    def test_security_risk_url(self):
        """ Test that the url is correct. """
        self.assertEqual('http://view', self.__jira.user_stories_without_security_risk_assessment_url())

    def test_performance_risk(self):
        """ Test that the correct number of user stories without performance risk assessment is returned. """
        self.assertEqual(5, self.__jira.nr_user_stories_without_performance_risk_assessment())

    def test_performance_risk_without_query(self):
        """ Test that the number of user stories is -1 when Jira hasn't got the right query. """
        self.assertEqual(-1, self.jira().nr_user_stories_without_performance_risk_assessment())

    def test_performance_risk_url(self):
        """ Test that the url is correct. """
        self.assertEqual('http://view', self.__jira.user_stories_without_performance_risk_assessment_url())


class JiraWhenFailingTest(JiraTestCase):
    """ Unit tests for a Jira that's unavailable. """

    url = 'http://raise'

    def setUp(self):
        self.__jira = self.jira(open_bug_query_id=123, open_security_bug_query_id=456, manual_test_cases_query_id=654,
                                technical_debt_issues_query_id=444, user_stories_ready_query_id=555,
                                user_stories_without_security_risk_query_id=567,
                                user_stories_without_performance_risk_query_id=789)

    def test_nr_open_bugs(self):
        """ Test that the number of open bugs is -1 when Jira is not available. """
        self.assertEqual(-1, self.__jira.nr_open_bugs())

    def test_nr_open_bugs_url(self):
        """ Test that the url is correct. """
        self.assertEqual(None, self.__jira.nr_open_bugs_url())

    def test_points_ready(self):
        """ Test that the total number points of ready user stories is -1 when Jira is not available. """
        self.assertEqual(-1, self.__jira.nr_story_points_ready())
