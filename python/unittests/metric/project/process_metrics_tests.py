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

from qualitylib import metric, domain, metric_source, requirement


class FakeJira(object):
    """ Fake Jira. """

    @staticmethod
    def nr_story_points_ready():
        """ Return a fake number of ready user story points. """
        return 7

    @staticmethod
    def user_stories_ready_url():
        """ Return a fake url for the nr of ready user story points query. """
        return 'http://readystories/'


class ReadyUserStoryPointsTest(unittest.TestCase):
    """ Unit tests for the number of ready user story points metric. """

    def setUp(self):
        self.__project = domain.Project(metric_sources={metric_source.Jira: FakeJira()},
                                        requirements=[requirement.TRACK_READY_US])
        self.__metric = metric.ReadyUserStoryPoints(project=self.__project)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(FakeJira.nr_story_points_ready(), self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({'Jira': FakeJira.user_stories_ready_url()}, self.__metric.url())

    def test_should_be_measured(self):
        """ Test that the metric should be measured when the project has the appropriate requirement. """
        self.assertTrue(metric.ReadyUserStoryPoints.should_be_measured(self.__project))
