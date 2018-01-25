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

import unittest
from unittest.mock import MagicMock
from hqlib import metric, domain, metric_source
from .bug_metrics_tests import FakeJiraFilter


class ProjectPrerequisitesTestCase(unittest.TestCase):
    """" Prerequisites tests for UserStoriesDurationTest and UserStoriesInProgress"""

    def test_project_for_user_stories_in_progress(self):
        """" Checks if the real objects fulfill requirements expected by LastSecurityTestCase """

        project = domain.Project()

        self.assertTrue(project is not None)
        self.assertTrue(callable(getattr(project, "metric_sources")))
        self.assertTrue(callable(getattr(project, "metric_source_id")))


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


class UserStoriesDurationTest(unittest.TestCase):
    """ Unit tests for duration of user stories. """

    def test_value(self):
        """ Test that the value is correct and rounded. """
        project = MagicMock()
        mock_metric_source = MagicMock()
        mock_metric_source.average_duration_of_issues.return_value = 2.33145
        project.metric_sources.return_value = [mock_metric_source]
        subject = MagicMock()
        subject.metric_source_id = MagicMock(return_value='src_id')
        duration_metric = metric.UserStoriesDuration(project=project, subject=subject)

        self.assertEqual(2.3, duration_metric.value())

    def test_extra_info(self):
        """ Test that the extra info object is the one of metric source. """
        expected_extra_info = object()
        project = MagicMock()
        mock_metric_source = MagicMock()
        mock_metric_source.extra_info.return_value = expected_extra_info
        project.metric_sources.return_value = [mock_metric_source]
        subject = MagicMock()
        subject.metric_source_id = MagicMock(return_value='src_id')
        duration_metric = metric.UserStoriesDuration(project=project, subject=subject)

        self.assertEqual(expected_extra_info, duration_metric.extra_info())

    def test_extra_info_no_metric_source(self):
        """ Test that the None is returned as extra info if there is no metric source. """

        project = MagicMock()
        project.metric_sources.return_value = [None]
        subject = MagicMock()
        subject.metric_source_id = MagicMock(return_value='src_id')
        duration_metric = metric.UserStoriesDuration(project=project, subject=subject)

        self.assertEqual(None, duration_metric.extra_info())

    def test_value_empty_metric_source(self):
        """ Test that the value method returns -1 if the metric source is None. """
        project = MagicMock()
        project.metric_sources.return_value = []
        subject = MagicMock()
        subject.metric_source_id.return_value = 'src_id'
        duration_metric = metric.UserStoriesDuration(project=project, subject=subject)

        self.assertEqual(-1, duration_metric.value())

    def test_report(self):
        """ Test that the report includes the total number of issues in the filter. """
        project = MagicMock()
        mock_metric_source = MagicMock()
        mock_metric_source.average_duration_of_issues.return_value = 2.5
        mock_metric_source.nr_issues.return_value = 10
        project.metric_sources.return_value = [mock_metric_source]
        subject = MagicMock()
        subject.metric_source_id.return_value = 'src_id'
        duration_metric = metric.UserStoriesDuration(project=project, subject=subject)

        self.assertEqual("10 user stories waren gemiddeld 2.5 dagen in progress.", duration_metric.report())


class UserStoriesInProgressTest(unittest.TestCase):
    """ Unit tests for the number of user stories in progress metric. """

    def test_value(self):
        """ Test that the value is correct. """
        project = MagicMock()
        mock_metric_source = MagicMock()
        mock_metric_source.nr_issues.return_value = 12
        project.metric_sources = MagicMock(return_value=[mock_metric_source])
        subject = MagicMock()
        subject.metric_source_id = MagicMock(return_value='src_id')
        progress_metric = metric.UserStoriesInProgress(project=project, subject=subject)

        self.assertEqual(12, progress_metric.value())

    def test_value_empty_metric_source(self):
        """ Test that the value method returns -1 if the metric source is None. """
        project = MagicMock()
        project.metric_sources = MagicMock(return_value=[None])
        subject = MagicMock()
        subject.metric_source_id = MagicMock(return_value='src_id')
        progress_metric = metric.UserStoriesInProgress(project=project, subject=subject)

        self.assertEqual(-1, progress_metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        project = MagicMock()
        mock_metric_source = MagicMock()
        mock_metric_source.metric_source_urls.return_value = ['http://filter/']
        mock_metric_source.metric_source_name = 'Jira filter'
        project.metric_sources = MagicMock(return_value=[mock_metric_source])
        subject = MagicMock()
        subject.metric_source_id = MagicMock(return_value='src_id')
        progress_metric = metric.UserStoriesInProgress(project=project, subject=subject)

        self.assertEqual({'Jira filter': 'http://filter/'}, progress_metric.url())


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
