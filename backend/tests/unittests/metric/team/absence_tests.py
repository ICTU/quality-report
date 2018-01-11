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

import datetime
import unittest

from hqlib import metric, domain, metric_source


class FakeHolidayPlanner(object):  # pylint: disable=too-few-public-methods
    """ Fake a holiday planner. """

    metric_source_name = metric_source.HolidayPlanner.metric_source_name

    def __init__(self):
        self.period = 6

    def days(self, team, start_date=None):  # pylint: disable=unused-argument
        """ Return the number of consecutive days more than one team member is absent. """
        period = 0 if start_date else self.period
        return period, datetime.date.today(), datetime.date.today() + datetime.timedelta(days=period), team.members()

    @staticmethod
    def url():
        """ Return the url for the holiday planner. """
        return 'http://planner'

    def metric_source_urls(self, *args):  # pylint: disable=unused-argument
        """ Return the urls for the metric source ids. """
        return [self.url()]


class TeamAbsenceTest(unittest.TestCase):
    """ Unit tests for the team absence metric. """

    def setUp(self):
        self.__planner = FakeHolidayPlanner()
        self.__project = domain.Project(metric_sources={metric_source.HolidayPlanner: self.__planner})
        self.__team = domain.Team(name='Team', metric_source_ids={self.__planner: "team"})
        self.__team.add_member(domain.Person(name='Piet Programmer'))
        self.__team.add_member(domain.Person(name='Derk Designer'))
        self.__metric = metric.TeamAbsence(self.__team, project=self.__project)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(6, self.__metric.value())

    def test_value_when_ignoring_near_future(self):
        """ Test that the near future can be ignored. """
        team = domain.Team(name='Team', metric_source_ids={self.__planner: "team"},
                           metric_options={metric.TeamAbsence: dict(start_date=datetime.date(9999, 1, 1))})
        absence = metric.TeamAbsence(team, project=self.__project)
        self.assertEqual(0, absence.value())

    def test_start_date_in_the_past(self):
        """ Test that a start date in the past is ignored. """
        team = domain.Team(name='Team', metric_options={
            metric.TeamAbsence: dict(start_date=datetime.date.today() - datetime.timedelta(days=10))})
        absence = metric.TeamAbsence(team, project=self.__project)
        self.assertNotEqual('Er zijn geen teamleden tegelijk gepland afwezig.', absence.report())

    def test_report(self):
        """ Test that the report is correct. """
        today = datetime.date.today()
        start = today.isoformat()
        end = (today + datetime.timedelta(days=6)).isoformat()
        self.assertEqual('De langste periode na vandaag dat meerdere teamleden tegelijk gepland afwezig zijn is 6 '
                         'werkdagen ({start} tot en met {end}). Afwezig zijn: Derk Designer, '
                         'Piet Programmer.'.format(start=start, end=end), self.__metric.report())

    def test_report_without_absence(self):
        """ Test that the report is correct when there are no absences. """
        self.__planner.period = 0
        self.assertEqual('Er zijn geen teamleden tegelijk gepland afwezig.', self.__metric.report())

    def test_url(self):
        """ Test that the url points to the url of the holiday planner. """
        self.assertEqual({FakeHolidayPlanner.metric_source_name: FakeHolidayPlanner.url()}, self.__metric.url())

    def test_is_applicable(self):
        """ Test that the metric is applicable. """
        self.assertTrue(metric.TeamAbsence(subject=self.__team, project=self.__project).is_applicable())

    def test_is_not_applicable(self):
        """ Test that the metric can't be measured without more than one team member. """
        team = domain.Team(name='Team')
        team.add_member(domain.Person(name='Piet Programmer'))
        self.assertFalse(metric.TeamAbsence(subject=team, project=self.__project).is_applicable())

    def test_default_norm(self):
        """ Test that the norm can be shown without instantiating the class. """
        defaults = metric.TeamAbsence.norm_template_default_values()
        self.assertEqual('Het aantal aaneengesloten werkdagen na vandaag dat meerdere teamleden tegelijk gepland '
                         'afwezig zijn is lager dan 5 werkdagen. Meer dan 10 werkdagen is rood. Het team bestaat uit '
                         '(Lijst van teamleden).', metric.TeamAbsence.norm_template.format(**defaults))

    def test_norm(self):
        """ Test that the norm is correct when the holiday planner hasn't been configured. """
        absence = metric.TeamAbsence(self.__team, project=domain.Project())
        self.assertEqual('Het aantal aaneengesloten werkdagen na vandaag dat meerdere teamleden tegelijk gepland '
                         'afwezig zijn is lager dan 5 werkdagen. Meer dan 10 werkdagen is rood. Het team bestaat '
                         'uit Derk Designer, Piet Programmer.', absence.norm())
