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

import unittest

from qualitylib import metric, domain, metric_source


class FakeJira(object):
    """ Fake Jira. """
    def __init__(self, has_queries=True):
        self.__has_queries = has_queries

    def has_open_bugs_query(self):
        """ Return whether Jira has an open bugs query. """
        return self.__has_queries

    @staticmethod
    def nr_open_bugs():
        """ Return a fake number of open bugs. """
        return 7

    @staticmethod
    def nr_open_bugs_url():
        """ Return a fake url for the nr of open bugs query. """
        return 'http://openbugs/'

    def has_open_security_bugs_query(self):
        """ Return whether Jira has an open security bugs query. """
        return self.__has_queries

    @staticmethod
    def nr_open_security_bugs():
        """ Return a fake number of open security bugs. """
        return 7

    @staticmethod
    def nr_open_security_bugs_url():
        """ Return a fake url for the nr of open security bugs query. """
        return 'http://opensecuritybugs/'

    def has_technical_debt_issues_query(self):
        """ Return whether Jira has a technical debt issues query. """
        return self.__has_queries

    @staticmethod
    def nr_technical_debt_issues_url():
        """ Return a fake url for the number of technical debt issues query. """
        return 'http://technicaldebtissues/'

    @staticmethod
    def nr_technical_debt_issues():
        """ Return the number of technical debt issues. """
        return 8


class OpenBugsTest(unittest.TestCase):
    """ Unit tests for the number of open bugs metric. """

    def setUp(self):
        self.__project = domain.Project(metric_sources={metric_source.Jira: FakeJira()})
        self.__metric = metric.OpenBugs(project=self.__project)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(FakeJira.nr_open_bugs(), self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({'Jira': FakeJira.nr_open_bugs_url()}, self.__metric.url())

    def test_can_be_measured(self):
        """ Test that the metric can be measured when the project has Jira,
            and Jira has an open bugs query. """
        self.assertTrue(metric.OpenBugs.can_be_measured(self.__project, self.__project))

    def test_cant_be_measured_without_jira(self):
        """ Test that the metric cannot be measured without Jira. """
        project = domain.Project()
        self.assertFalse(metric.OpenBugs.can_be_measured(self.__project, project))

    def test_cant_be_measured_without_open_bugs_query(self):
        """ Test that the metric cannot be measured without an open bugs query in Jira. """
        project = domain.Project(metric_sources={metric_source.Jira: FakeJira(has_queries=False)})
        self.assertFalse(metric.OpenBugs.can_be_measured(self.__project, project))


class OpenSecurityBugsTest(unittest.TestCase):
    """ Unit tests for the number of open security bugs metric. """

    def setUp(self):
        self.__project = domain.Project(metric_sources={metric_source.Jira: FakeJira()})
        self.__metric = metric.OpenSecurityBugs(project=self.__project)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(FakeJira.nr_open_security_bugs(), self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({'Jira': FakeJira.nr_open_security_bugs_url()}, self.__metric.url())

    def test_can_be_measured(self):
        """ Test that the metric can be measured when the project has Jira, and Jira has an open bugs query. """
        self.assertTrue(metric.OpenSecurityBugs.can_be_measured(self.__project, self.__project))

    def test_cant_be_measured_without_jira(self):
        """ Test that the metric cannot be measured without Jira. """
        project = domain.Project()
        self.assertFalse(metric.OpenSecurityBugs.can_be_measured(self.__project, project))

    def test_cant_be_measured_without_open_bugs_query(self):
        """ Test that the metric cannot be measured without an open bugs query in Jira. """
        jira = FakeJira(has_queries=False)
        project = domain.Project(metric_sources={metric_source.Jira: jira})
        self.assertFalse(metric.OpenSecurityBugs.can_be_measured(self.__project, project))


class TechnicalDebtIssuesTest(unittest.TestCase):
    """ Unit tests for the number of technical debt issues metric. """

    def setUp(self):
        self.__project = domain.Project(metric_sources={metric_source.Jira: FakeJira()})
        self.__metric = metric.TechnicalDebtIssues(project=self.__project)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(FakeJira.nr_technical_debt_issues(), self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({'Jira': FakeJira.nr_technical_debt_issues_url()}, self.__metric.url())

    def test_can_be_measured(self):
        """ Test that the metric can be measured when the project has Jira,
            and Jira has a technical debt issue query. """
        self.assertTrue(metric.TechnicalDebtIssues.can_be_measured(self.__project, self.__project))

    def test_cant_be_measured_without_jira(self):
        """ Test that the metric cannot be measured without Jira. """
        project = domain.Project()
        self.assertFalse(metric.TechnicalDebtIssues.can_be_measured(self.__project, project))

    def test_cant_be_measured_without_td_issues_query(self):
        """ Test that the metric cannot be measured without a technical debt issues query in Jira. """
        jira = FakeJira(has_queries=False)
        project = domain.Project(metric_sources={metric_source.Jira: jira})
        self.assertFalse(metric.TechnicalDebtIssues.can_be_measured(self.__project, project))
