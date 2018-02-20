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
        self.__project = unittest.mock.create_autospec(domain.Project, instance=True)
        self.__subject = MagicMock()
        self.__subject.metric_source_id.return_value = "src_id"

    def test_norm(self):
        """ Test that the norm is correct. """
        self.__subject.target.return_value = 20
        self.__subject.low_target.return_value = 10
        duration_metric = metric.ReadyUserStoryPoints(project=self.__project, subject=self.__subject)

        self.assertEqual("Minimaal 20 ready user story punten. "
                         "Minder dan 10 ready user story punten is rood.", duration_metric.norm())

    def test_value(self):
        """ Test that the value is correct. """
        mock_metric_source = MagicMock()
        mock_metric_source.sum_field.return_value = 120
        self.__project.metric_sources.return_value = [mock_metric_source]
        ready_metric = metric.ReadyUserStoryPoints(project=self.__project, subject=self.__subject)

        self.assertEqual(120, ready_metric.value())


class UserStoriesDurationTest(unittest.TestCase):
    """ Unit tests for duration of user stories. """

    def setUp(self):
        self.__project = unittest.mock.create_autospec(domain.Project, instance=True)
        self.__subject = MagicMock()
        self.__subject.metric_source_id.return_value = "src_id"

    def test_value(self):
        """ Test that the value is correct and rounded. """
        mock_metric_source = MagicMock()
        mock_metric_source.average_duration_of_issues.return_value = 2.33145
        self.__project.metric_sources.return_value = [mock_metric_source]
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        self.assertEqual(2.3, duration_metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        mock_metric_source = MagicMock()
        mock_metric_source.average_duration_of_issues.return_value = 2.33145
        mock_metric_source.nr_issues.return_value = 10
        self.__project.metric_sources.return_value = [mock_metric_source]
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        self.assertEqual("10 user stories waren 2.3 dagen gemiddeld in progress.", duration_metric.report())

    def test_norm(self):
        """ Test that the norm is correct. """
        self.__subject.target.return_value = 5
        self.__subject.low_target.return_value = 7
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        self.assertEqual("User stories zijn maximaal 5 dagen gemiddeld in progress. "
                         "Meer dan 7 dagen gemiddeld in progress is rood.", duration_metric.norm())

    def test_extra_info(self):
        """ Test that the extra info object is the one of metric source. """
        expected_extra_info = object()
        mock_metric_source = MagicMock()
        mock_metric_source.extra_info.return_value = expected_extra_info
        self.__project.metric_sources.return_value = [mock_metric_source]
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        self.assertEqual(expected_extra_info, duration_metric.extra_info())

    def test_extra_info_no_metric_source(self):
        """ Test that the None is returned as extra info if there is no metric source. """
        self.__project.metric_sources.return_value = []
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        self.assertEqual(None, duration_metric.extra_info())

    def test_value_empty_metric_source(self):
        """ Test that the value method returns -1 if the metric source is None. """
        self.__project.metric_sources.return_value = [None]
        duration_metric = metric.UserStoriesDuration(project=self.__project, subject=self.__subject)

        self.assertEqual(-1, duration_metric.value())


class UserStoriesInProgressTest(unittest.TestCase):
    """ Unit tests for the number of user stories in progress metric. """

    def setUp(self):
        self.__project = unittest.mock.create_autospec(domain.Project, instance=True)
        self.__subject = MagicMock()

    def test_norm(self):
        """ Test that the norm is correct. """
        self.__subject.target.return_value = 5
        self.__subject.low_target.return_value = 7
        progress_metric = metric.UserStoriesInProgress(project=self.__project, subject=self.__subject)

        self.assertEqual("Maximaal 5 stories in progress. Meer dan 7 stories in progress is rood.",
                         progress_metric.norm())

    def test_value(self):
        """ Test that the value is correct. """
        mock_metric_source = MagicMock()
        mock_metric_source.nr_issues.return_value = 12
        self.__project.metric_sources = MagicMock(return_value=[mock_metric_source])
        progress_metric = metric.UserStoriesInProgress(project=self.__project, subject=self.__subject)

        self.assertEqual(12, progress_metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        mock_metric_source = MagicMock()
        mock_metric_source.nr_issues.return_value = 12
        self.__project.metric_sources = MagicMock(return_value=[mock_metric_source])
        self.__subject.name.return_value = "Foo"
        progress_metric = metric.UserStoriesInProgress(project=self.__project, subject=self.__subject)

        self.assertEqual("Foo heeft 12 stories in progress.", progress_metric.report())

    def test_status(self):
        """ Test that the status is correct. """
        mock_metric_source = MagicMock()
        mock_metric_source.nr_issues.return_value = 3
        self.__project.metric_sources = MagicMock(return_value=[mock_metric_source])
        self.__subject.target.return_value = None
        self.__subject.low_target.return_value = None
        progress_metric = metric.UserStoriesInProgress(project=self.__project, subject=self.__subject)

        self.assertEqual("green", progress_metric.status())

    def test_value_empty_metric_source(self):
        """ Test that the value method returns -1 if the metric source is None. """
        self.__project.metric_sources = MagicMock(return_value=[None])
        progress_metric = metric.UserStoriesInProgress(project=self.__project, subject=self.__subject)

        self.assertEqual(-1, progress_metric.value())


class UserStoriesWithoutSecurityRiskTest(unittest.TestCase):
    """ Unit tests for the number of user stories without security risk assessment metric. """

    def setUp(self):
        jira = FakeJiraFilter()
        self.__project = domain.Project(
            metric_sources={metric_source.UserStoryWithoutSecurityRiskAssessmentTracker: jira},
            metric_source_ids={jira: '12345'})
        self.__metric = metric.UserStoriesWithoutSecurityRiskAssessment(project=self.__project, subject=self.__project)

    def test_norm(self):
        """ Test that the norm is correct. """
        self.assertEqual("Maximaal 1 ready user stories zonder security risk beoordeling. "
                         "Meer dan 3 ready user stories zonder security risk beoordeling is rood.",
                         self.__metric.norm())

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(12, self.__metric.value())

    def test_report(self):
        """ Test that the report of the metric is correct. """
        mock_metric_source = MagicMock()
        mock_metric_source.nr_issues.return_value = 5
        project = unittest.mock.create_autospec(domain.Project, instance=True)
        project.metric_sources.return_value = [mock_metric_source]
        subject = MagicMock()
        assessment_metric = metric.UserStoriesWithoutSecurityRiskAssessment(project=project, subject=subject)

        self.assertEqual("Het aantal ready user stories zonder security risk beoordeling is 5.",
                         assessment_metric.report())


class UserStoriesWithoutPerformanceRiskTest(unittest.TestCase):
    """ Unit tests for the number of user stories without performance risk assessment metric. """

    def setUp(self):
        jira = FakeJiraFilter()
        self.__project = domain.Project(
            metric_sources={metric_source.UserStoryWithoutPerformanceRiskAssessmentTracker: jira},
            metric_source_ids={jira: '12345'})
        self.__metric = metric.UserStoriesWithoutPerformanceRiskAssessment(project=self.__project,
                                                                           subject=self.__project)

    def test_norm(self):
        """ Test that the norm is correct. """
        self.assertEqual("Maximaal 1 ready user stories zonder performance risk beoordeling. "
                         "Meer dan 3 ready user stories zonder performance risk beoordeling is rood.",
                         self.__metric.norm())

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(12, self.__metric.value())
