'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

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
        return StringIO.StringIO( \
            '{"searchUrl": "http://search", "viewUrl": "%s", "total": %d, ' \
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
                                    jira_project_id=99,
                                    jira_parent_task_id=1234)

    def test_url(self):
        ''' Test the Jira url. '''
        self.assertEqual(self.__jira_url, self.__jira.url())

    def test_has_open_bugs_query(self):
        ''' Test that the Jira under test has an open bugs query. '''
        self.failUnless(self.__jira.has_open_bugs_query())

    def test_nr_open_bugs(self):
        ''' Test that the number of open bugs is correct. '''
        self.assertEqual(self.__jira.NR_QUERY_RESULTS, 
                         self.__jira.nr_open_bugs())

    def test_nr_open_bugs_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(self.__jira.VIEW_URL, self.__jira.nr_open_bugs_url())

    def test_has_open_security_bugs_query(self):
        ''' Test that the Jira under test has an open security bugs query. '''
        self.failUnless(self.__jira.has_open_security_bugs_query())

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
        self.failUnless(self.__jira.has_blocking_test_issues_query())

    def test_blocking_test_issues(self):
        ''' Test that the number of blocking test issues is correct. '''
        self.assertEqual(self.__jira.NR_QUERY_RESULTS,
                         self.__jira.nr_blocking_test_issues())

    def test_test_issues_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(self.__jira.VIEW_URL, 
                         self.__jira.nr_blocking_test_issues_url())

    def test_no_tasks(self):
        ''' Test there are no tasks by default. '''
        self.failIf(self.__jira.tasks('K1'))

    def test_one_task(self):
        ''' Test one task. '''
        JiraUnderTest.ISSUES = '[{"key": "I1", ' \
                               '"fields": {"description": "Metriek K1"}}]'
        self.assertEqual(['http://jira/browse/I1'], self.__jira.tasks('K1'))

    def test_one_recent_task(self):
        ''' Test one recent task. '''
        now = datetime.datetime.now()
        JiraUnderTest.ISSUES = '[{"key": "I1", ' \
                               '"fields": {"description": "Metriek K1", ' \
                               '"updated": "%s"}}]' % \
                               now.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        self.assertEqual(['http://jira/browse/I1'], 
                         self.__jira.tasks('K1', recent_only=True))

    def test_default_new_task_url(self):
        ''' Test the default url for creating new tasks. '''
        self.assertEqual('http://jira/&description=Metriek+K1', 
                         JiraUnderTest(self.__jira_url, 'username', 
                                       'password').new_task_url('K1'))

    def test_new_task_url(self):
        ''' Test the url for creating new tasks. '''
        self.assertEqual('http://jira/secure/CreateSubTaskIssue!default.jspa' \
            '?pid=99&issuetype=8&parentIssueId=1234&description=Metriek+K1', 
            self.__jira.new_task_url('K1'))
