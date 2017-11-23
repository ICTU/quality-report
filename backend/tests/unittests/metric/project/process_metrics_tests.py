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

from hqlib import metric, domain, metric_source

from .bug_metrics_tests import FakeJiraFilter


class ReadyUserStoryPointsTest(unittest.TestCase):
    """ Unit tests for the number of ready user story points metric. """

    def setUp(self):
        jira = FakeJiraFilter()
        project = domain.Project(metric_sources={metric_source.ReadyUserStoryPointsTracker: jira},
                                 metric_source_ids={jira: '12345'})
        self.__metric = metric.ReadyUserStoryPoints(project=project, subject=project)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(120, self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({'Jira filter': 'http://filter/'}, self.__metric.url())


class UserStoriesWithoutSecurityRiskTest(unittest.TestCase):
    """ Unit tests for the number of user stories without security risk assessment metric. """

    def setUp(self):
        jira = FakeJiraFilter()
        self.__project = domain.Project(
            metric_sources={metric_source.UserStoryWithoutSecurityRiskAssessmentTracker: jira},
            metric_source_ids={jira: '12345'})
        self.__metric = metric.UserStoriesWithoutSecurityRiskAssessment(project=self.__project, subject=self.__project)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(12, self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({'Jira filter': 'http://filter/'}, self.__metric.url())


class UserStoriesWithoutPerformanceRiskTest(unittest.TestCase):
    """ Unit tests for the number of user stories without performance risk assessment metric. """

    def setUp(self):
        jira = FakeJiraFilter()
        self.__project = domain.Project(
            metric_sources={metric_source.UserStoryWithoutPerformanceRiskAssessmentTracker: jira},
            metric_source_ids={jira: '12345'})
        self.__metric = metric.UserStoriesWithoutPerformanceRiskAssessment(project=self.__project,
                                                                           subject=self.__project)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(12, self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({'Jira filter': 'http://filter/'}, self.__metric.url())
