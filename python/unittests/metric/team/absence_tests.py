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

import datetime
import unittest

from qualitylib import metric, domain, metric_source


class FakeHolidayPlanner(object):  # pylint: disable=too-few-public-methods
    """ Fake a holiday planner. """

    def __init__(self):
        self.period = 6

    def days(self, team):  # pylint: disable=unused-argument
        """ Return the number of consecutive days more than one team member is absent. """
        return (self.period, datetime.date.today(), datetime.date.today() + datetime.timedelta(days=self.period),
                team.members())

    @staticmethod
    def url():
        """ Return the url for the holiday planner. """
        return 'http://planner'


class TeamAbsenceTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the team absence metric. """

    def setUp(self):  # pylint: disable=invalid-name
        self.__planner = FakeHolidayPlanner()
        self.__project = domain.Project(metric_sources={metric_source.HolidayPlanner: self.__planner})
        self.__team = domain.Team(name='Team')
        self.__team.add_member(domain.Person(name='Piet Programmer'))
        self.__team.add_member(domain.Person(name='Derk Designer'))
        self.__metric = metric.TeamAbsence(self.__team, project=self.__project)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(6, self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        today = datetime.date.today()
        start = today.isoformat()
        end = (today + datetime.timedelta(days=6)).isoformat()
        self.assertEqual('De langste periode dat meerdere teamleden tegelijk gepland afwezig zijn is 6 werkdagen '
                         '(%s tot en met %s). Afwezig zijn: Derk Designer, Piet Programmer.' % (start, end),
                         self.__metric.report())

    def test_report_without_absence(self):
        """ Test that the report is correct when there are no absences. """
        self.__planner.period = 0
        self.assertEqual('Er zijn geen teamleden tegelijk gepland afwezig.', self.__metric.report())

    def test_url(self):
        """ Test that the url points to the url of the holiday planner. """
        self.assertEqual(dict(Planner=FakeHolidayPlanner.url()), self.__metric.url())

    def test_can_be_measured(self):
        """ Test that the metric can be measured when the project has a holiday planner. """
        self.assertTrue(metric.TeamAbsence.can_be_measured(self.__team, self.__project))

    def test_cant_be_measured_without_holiday_planner(self):
        """ Test that the metric can't be measured without a holiday planner metric source. """
        project = domain.Project()
        self.assertFalse(metric.TeamAbsence.can_be_measured(self.__team, project))

    def test_cant_be_measured_without_enough_members(self):
        """ Test that the metric can't be measured without more than one team member. """
        team = domain.Team(name='Team')
        team.add_member(domain.Person(name='Piet Programmer'))
        self.assertFalse(metric.TeamAbsence.can_be_measured(team, self.__project))

    def test_default_norm(self):
        """ Test that the norm can be shown without instantiating the class. """
        defaults = metric.TeamAbsence.norm_template_default_values()
        self.assertEqual('Het aantal aaneengesloten dagen dat meerdere teamleden tegelijk gepland afwezig zijn is '
                         'lager dan 5 werkdagen. Meer dan 10 werkdagen is rood. Het team bestaat uit '
                         '(Lijst van teamleden).', metric.TeamAbsence.norm_template.format(**defaults))
