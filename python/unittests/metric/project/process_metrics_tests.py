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

    def has_user_stories_ready_query(self):
        """ Return whether Jira has an ready user stories query. """
        return self.__has_queries

    @staticmethod
    def nr_story_points_ready():
        """ Return a fake number of ready user story points. """
        return 7

    @staticmethod
    def user_stories_ready_url():
        """ Return a fake url for the nr of ready user story points query. """
        return 'http://readystories/'


class ReadyUserStoryPointsTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the number of ready user story points metric. """

    def setUp(self):
        self.__project = domain.Project(metric_sources={metric_source.Jira: FakeJira()})
        self.__metric = metric.ReadyUserStoryPoints(project=self.__project)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(FakeJira.nr_story_points_ready(), self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({'Jira': FakeJira.user_stories_ready_url()}, self.__metric.url())

    def test_can_be_measured(self):
        """ Test that the metric can be measured when the project has Jira,
            and Jira has an ready user stories query. """
        self.assertTrue(metric.ReadyUserStoryPoints.can_be_measured(self.__project, self.__project))

    def test_cant_be_measured_without_jira(self):
        """ Test that the metric cannot be measured without Jira. """
        project = domain.Project()
        self.assertFalse(metric.ReadyUserStoryPoints.can_be_measured(self.__project, project))

    def test_cant_be_measured_without_ready_us_query(self):
        """ Test that the metric cannot be measured without an ready user stories query in Jira. """
        project = domain.Project(metric_sources={metric_source.Jira: FakeJira(has_queries=False)})
        self.assertFalse(metric.ReadyUserStoryPoints.can_be_measured(self.__project, project))
