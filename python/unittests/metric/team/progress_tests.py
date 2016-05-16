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


class FakeBirt(object):
    """ Fake Birt so we can return fake velocity information. """
    # pylint: disable=unused-argument

    @staticmethod
    def planned_velocity(birt_id):
        """ Return the planned velocity of the team. """
        return 1

    @staticmethod
    def actual_velocity(birt_id):
        """ Return the actual velocity of the team so far. """
        return 0.5

    @staticmethod
    def required_velocity(birt_id):
        """ Return the required velocity of the team. """
        return 2

    @staticmethod
    def nr_points_planned(birt_id):
        """ Return the number of points planned for the sprint. """
        return 20

    @staticmethod
    def nr_points_realized(birt_id):
        """ Return the number of points realized so far. """
        return 10

    @staticmethod
    def days_in_sprint(birt_id):
        """ Return the number of working days in the sprint. """
        return 20

    @staticmethod
    def day_in_sprint(birt_id):
        """ Return the current day in the sprint. """
        return 10

    @staticmethod
    def sprint_progress_url(birt_id):
        """ Return the url of the sprint progress report. """
        return 'http://birt/report/'


class TeamProgressTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the team progress metric. """

    def setUp(self):  # pylint: disable=invalid-name
        self.__birt = FakeBirt()
        self.__team = domain.Team(name='ABC', is_scrum_team=True, metric_source_ids={self.__birt: 'abc'})
        self.__project = domain.Project(metric_sources={metric_source.Birt: self.__birt})
        self.__metric = metric.TeamProgress(subject=self.__team, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric equals the required velocity. """
        self.assertEqual(2, self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual('Team ABC heeft een velocity van 2.0 punt per dag nodig om het sprintdoel van de huidige '
                         'sprint (20.0 punten) te halen. De geplande velocity is 1.0 punt per dag. De tot nu toe '
                         '(dag 10 van 20) gerealiseerde velocity is 0.5 punt per dag (10.0 punten).',
                         self.__metric.report())

    def test_url(self):
        """ Test that the url of the metric is the url of the Birt report. """
        self.assertEqual(dict(Birt='http://birt/report/'), self.__metric.url())

    def test_can_be_measured(self):
        """ Test that the metric can be measured if the project has Birt and the team has a Birt id. """
        self.assertTrue(metric.TeamProgress.can_be_measured(self.__team, self.__project))

    def test_can_only_be_measured_for_scrum_teams(self):
        """ Test that the metric cannot be measured if the team is not a Scrum team. """
        team = domain.Team(name='ABC', metric_source_ids={self.__birt: 'abc'})
        self.assertFalse(metric.TeamProgress.can_be_measured(team, self.__project))

    def test_cant_be_measured_without_birt_id(self):
        """ Test that the metric cannot be measured if the team has no Birt id. """
        team = domain.Team(name='Team', is_scrum_team=True)
        self.assertFalse(metric.TeamProgress.can_be_measured(team, self.__project))

    def test_cant_be_measured_without_birt(self):
        """ Test that the metric cannot be measured without Birt. """
        project = domain.Project()
        self.assertFalse(metric.TeamProgress.can_be_measured(self.__team, project))

    def test_norm_template_default_values(self):
        """ Test that the right values are returned to fill in the norm template. """
        self.assertTrue(metric.TeamProgress.norm_template % metric.TeamProgress.norm_template_default_values())
