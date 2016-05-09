'''
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
'''

import datetime
import unittest
import StringIO
from qualitylib.metric_source import Jira


class JiraUnderTest(Jira):
    ''' Override class to return a fixed JSON file. '''

    NR_QUERY_RESULTS = 5
    VIEW_URL = 'http://view'
    ISSUES = '[]'

    def url_open(self, url):
        return StringIO.StringIO(
            '{"searchUrl": "http://search", "viewUrl": "%s", "total": %d, '
            '"issues": %s}' % (self.VIEW_URL, self.NR_QUERY_RESULTS,
                               self.ISSUES))


class JiraTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the Jira class. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__jira_url = 'http://jira/'
        self.__jira = JiraUnderTest(self.__jira_url, 'username', 'password', 
                                    open_bug_query_id=123,
                                    open_security_bug_query_id=456,
                                    blocking_test_issues_query_id=321,
                                    manual_test_cases_query_id=654,
                                    technical_debt_issues_query_id=444,
                                    user_stories_ready_query_id=555)

    def test_url(self):
        ''' Test the Jira url. '''
        self.assertEqual(self.__jira_url, self.__jira.url())

    def test_has_open_bugs_query(self):
        ''' Test that the Jira under test has an open bugs query. '''
        self.assertTrue(self.__jira.has_open_bugs_query())

    def test_nr_open_bugs(self):
        ''' Test that the number of open bugs is correct. '''
        self.assertEqual(self.__jira.NR_QUERY_RESULTS, 
                         self.__jira.nr_open_bugs())

    def test_nr_open_bugs_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(self.__jira.VIEW_URL, self.__jira.nr_open_bugs_url())

    def test_has_open_security_bugs_query(self):
        ''' Test that the Jira under test has an open security bugs query. '''
        self.assertTrue(self.__jira.has_open_security_bugs_query())

    def test_nr_open_security_bugs(self):
        ''' Test that the number of open security bugs is correct. '''
        self.assertEqual(self.__jira.NR_QUERY_RESULTS, 
                         self.__jira.nr_open_security_bugs())

    def test_nr_open_security_bugs_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(self.__jira.VIEW_URL, 
                         self.__jira.nr_open_security_bugs_url())

    def test_has_test_issues_query(self):
        ''' Test that the Jira under test has a blocking test issues query. '''
        self.assertTrue(self.__jira.has_blocking_test_issues_query())

    def test_blocking_test_issues(self):
        ''' Test that the number of blocking test issues is correct. '''
        self.assertEqual(self.__jira.NR_QUERY_RESULTS,
                         self.__jira.nr_blocking_test_issues())

    def test_test_issues_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(self.__jira.VIEW_URL, 
                         self.__jira.nr_blocking_test_issues_url())

    def test_has_manual_tests_query(self):
        ''' Test that the Jira under test has a manual test cases query. '''
        self.assertTrue(self.__jira.has_manual_test_cases_query())

    def test_nr_manual_tests(self):
        ''' Test that the correct number of manual test cases is returned. '''
        self.assertEqual(5, self.__jira.nr_manual_test_cases())

    def test_manual_test_time(self):
        ''' Test that the total number of minutes spend on manual test cases is correct. '''
        self.__jira.ISSUES = '[{"fields": {"customfield_11700": "20"}},' \
                             ' {"fields": {"customfield_11700": 100}},' \
                             ' {"fields": {"customfield_11700": null}}]'
        self.assertEqual(120, self.__jira.manual_test_cases_time())

    def test_nr_manual_tests_not_measured(self):
        ''' Test that the number of manual test cases not measured is correct. '''
        self.__jira.ISSUES = '[{"fields": {"customfield_11700": "20"}},' \
                             ' {"fields": {"customfield_11700": 100}},' \
                             ' {"fields": {"customfield_11700": null}}]'
        self.assertEqual(1, self.__jira.nr_manual_test_cases_not_measured())

    def test_manual_test_time_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(self.__jira.VIEW_URL, self.__jira.manual_test_cases_url())

    def test_points_ready(self):
        ''' Test that the total number points of ready user stories is correct. '''
        self.__jira.ISSUES = '[{"fields": {"customfield_10002": "1.0"}},' \
                             ' {"fields": {"customfield_10002": "8.0"}},' \
                             ' {"fields": {"customfield_10002": null}}]'
        self.assertEqual(9, self.__jira.nr_story_points_ready())

    def test_technical_debt_issues(self):
        ''' Test that the Jira under test has a technical debt issues query. '''
        self.assertTrue(self.__jira.has_technical_debt_issues_query())

    def test_nr_technical_debt_issues(self):
        ''' Test that the correct number of technical debt issues is returned. '''
        self.assertEqual(5, self.__jira.nr_technical_debt_issues())

    def test_technical_debt_issues_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(self.__jira.VIEW_URL, self.__jira.nr_technical_debt_issues_url())

    def test_user_stories_ready(self):
        ''' Test that the Jira under test has a user stories ready query. '''
        self.assertTrue(self.__jira.has_user_stories_ready_query())

    def test_user_stories_ready_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(self.__jira.VIEW_URL, self.__jira.user_stories_ready_url())
