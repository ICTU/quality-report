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

import unittest

from hqlib import metric, domain, metric_source, requirement


class FakeJiraFilter(object):
    """ Fake Jira filter. """

    metric_source_name = metric_source.JiraFilter.metric_source_name
    needs_metric_source_id = metric_source.JiraFilter.needs_metric_source_id

    # pylint: disable=unused-argument

    @staticmethod
    def nr_issues(*metric_source_ids):
        """ Return a fake number of issues. """
        return 12

    @staticmethod
    def metric_source_urls(*metric_source_ids):
        """ Return a fake url for each query. """
        return ['http://filter/']


class OpenBugsTest(unittest.TestCase):
    """ Unit tests for the number of open bugs metric. """

    def setUp(self):
        jira = FakeJiraFilter()
        self.__project = domain.Project(metric_sources={metric_source.BugTracker: jira},
                                        metric_source_ids={jira: '1234'},
                                        requirements=[requirement.TrackBugs])
        self.__metric = metric.OpenBugs(project=self.__project, subject=self.__project)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(FakeJiraFilter.nr_issues(), self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({FakeJiraFilter.metric_source_name: FakeJiraFilter.metric_source_urls()[0]},
                         self.__metric.url())


class OpenBugsWithProductTest(unittest.TestCase):
    """ Unit tests for the number of open bugs metric applied to products. """

    def setUp(self):
        jira = FakeJiraFilter()
        self.__project = domain.Project(metric_sources={metric_source.BugTracker: jira})
        self.__product = domain.Product(metric_source_ids={jira: '1234'},
                                        added_requirements=[requirement.TrackBugs])
        self.__metric = metric.OpenBugs(project=self.__project, subject=self.__product)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(FakeJiraFilter.nr_issues(), self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({FakeJiraFilter.metric_source_name: FakeJiraFilter.metric_source_urls()[0]},
                         self.__metric.url())


class OpenSecurityBugsTest(unittest.TestCase):
    """ Unit tests for the number of open security bugs metric. """

    def setUp(self):
        jira = FakeJiraFilter()
        self.__project = domain.Project(metric_sources={metric_source.SecurityBugTracker: jira},
                                        metric_source_ids={jira: '1234'},
                                        requirements=[requirement.TrackBugs])
        self.__metric = metric.OpenSecurityBugs(project=self.__project, subject=self.__project)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(FakeJiraFilter.nr_issues(), self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({FakeJiraFilter.metric_source_name: FakeJiraFilter.metric_source_urls()[0]},
                         self.__metric.url())


class OpenSecurityBugsWithProductTest(unittest.TestCase):
    """ Unit tests for the number of open security bugs metric applied to products. """

    def setUp(self):
        jira = FakeJiraFilter()
        self.__project = domain.Project(metric_sources={metric_source.SecurityBugTracker: jira},
                                        metric_source_ids={jira: '1234'},
                                        requirements=[requirement.TrackBugs])
        self.__product = domain.Product(metric_source_ids={jira: '1234'},
                                        added_requirements=[requirement.TrackSecurityBugs])
        self.__metric = metric.OpenSecurityBugs(project=self.__project, subject=self.__product)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(FakeJiraFilter.nr_issues(), self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({FakeJiraFilter.metric_source_name: FakeJiraFilter.metric_source_urls()[0]},
                         self.__metric.url())


class OpenStaticSecurityAnalysisBugsTest(unittest.TestCase):
    """ Unit tests for the number of open static security analysis bugs metric. """

    def setUp(self):
        jira = FakeJiraFilter()
        self.__project = domain.Project(metric_sources={metric_source.StaticSecurityBugTracker: jira},
                                        metric_source_ids={jira: '1234'},
                                        requirements=[requirement.TrackBugs])
        self.__metric = metric.OpenStaticSecurityAnalysisBugs(project=self.__project, subject=self.__project)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(FakeJiraFilter.nr_issues(), self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({FakeJiraFilter.metric_source_name: FakeJiraFilter.metric_source_urls()[0]},
                         self.__metric.url())


class TechnicalDebtIssuesTest(unittest.TestCase):
    """ Unit tests for the number of technical debt issues metric. """

    def setUp(self):
        jira = FakeJiraFilter()
        self.__project = domain.Project(metric_sources={metric_source.TechnicalDebtTracker: jira},
                                        metric_source_ids={jira: '1234'},
                                        requirements=[requirement.TrackTechnicalDebt])
        self.__metric = metric.TechnicalDebtIssues(project=self.__project, subject=self.__project)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(FakeJiraFilter().nr_issues(), self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({'Jira filter': FakeJiraFilter.metric_source_urls()[0]}, self.__metric.url())
