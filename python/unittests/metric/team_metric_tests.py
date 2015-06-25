'''
Copyright 2012-2015 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from qualitylib import metric, domain, metric_source
import datetime
import unittest


class FakeBirt(object):
    ''' Fake Birt so we can return fake velocity information. '''
    # pylint: disable=unused-argument

    @staticmethod
    def planned_velocity(birt_id):
        ''' Return the planned velocity of the team. '''
        return 1

    @staticmethod
    def actual_velocity(birt_id):
        ''' Return the actual velocity of the team so far. '''
        return 0.5

    @staticmethod
    def required_velocity(birt_id):
        ''' Return the required velocity of the team. '''
        return 2

    @staticmethod
    def nr_points_planned(birt_id):
        ''' Return the number of points planned for the sprint. '''
        return 20

    @staticmethod
    def nr_points_realized(birt_id):
        ''' Return the number of points realized so far. '''
        return 10

    @staticmethod
    def days_in_sprint(birt_id):
        ''' Return the number of working days in the sprint. '''
        return 20

    @staticmethod
    def day_in_sprint(birt_id):
        ''' Return the current day in the sprint. '''
        return 10

    @staticmethod
    def sprint_progress_url(birt_id):
        ''' Return the url of the sprint progress report. '''
        return 'http://birt/report/'


class TeamProgressTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the team progress metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__birt = FakeBirt()
        self.__team = domain.Team(name='ABC', is_scrum_team=True,
                                  metric_source_ids={self.__birt: 'abc'})
        self.__project = domain.Project(metric_sources={metric_source.Birt: 
                                                        self.__birt})
        self.__metric = metric.TeamProgress(subject=self.__team, 
                                            project=self.__project)

    def test_value(self):
        ''' Test that the value of the metric equals the required velocity. '''
        self.assertEqual(2, self.__metric.value())

    def test_report(self):
        ''' Test that the report is correct. '''
        self.assertEqual('Team ABC heeft een velocity van 2.0 punt per dag '\
                         'nodig om het sprintdoel van de huidige sprint ' \
                         '(20.0 punten) te halen. De geplande velocity is ' \
                         '1.0 punt per dag. De tot nu toe (dag 10 van 20) ' \
                         'gerealiseerde velocity is 0.5 punt per dag ' \
                         '(10.0 punten).', self.__metric.report())

    def test_url(self):
        ''' Test that the url of the metric is the url of the Birt report. '''
        self.assertEqual(dict(Birt='http://birt/report/'), self.__metric.url())

    def test_can_be_measured(self):
        ''' Test that the metric can be measured if the project has Birt and
            the team has a Birt id. '''
        self.assertTrue(metric.TeamProgress.can_be_measured(self.__team,
                                                            self.__project))

    def test_can_only_be_measured_for_scrum_teams(self):
        ''' Test that the metric cannot be measured if the team is not a Scrum
            team. '''
        team = domain.Team(name='ABC', metric_source_ids={self.__birt: 'abc'})
        self.assertFalse(metric.TeamProgress.can_be_measured(team, self.__project))

    def test_cant_be_measured_without_birt_id(self):
        ''' Test that the metric cannot be measured if the team has no Birt 
            id. '''
        team = domain.Team(name='Team', is_scrum_team=True)
        self.assertFalse(metric.TeamProgress.can_be_measured(team, self.__project))

    def test_cant_be_measured_without_birt(self):
        ''' Test that the metric cannot be measured without Birt. '''
        project = domain.Project()
        self.assertFalse(metric.TeamProgress.can_be_measured(self.__team, project))

    def test_norm_template_default_values(self):
        ''' Test that the right values are returned to fill in the norm 
            template. '''
        self.assertTrue(metric.TeamProgress.norm_template % \
                        metric.TeamProgress.norm_template_default_values())


class FakeWiki(object):
    ''' Fake a wiki metric source. '''

    def __init__(self):
        self.date_of_last_measurement = datetime.datetime.now()

    @staticmethod  # pylint: disable=unused-argument
    def team_spirit(*args):
        ''' Return a fake team spirit. '''
        return ':-)'

    def date_of_last_team_spirit_measurement(self, *args):
        # pylint: disable=unused-argument, invalid-name
        ''' Return a fake date. '''
        return self.date_of_last_measurement

    @staticmethod
    def url():
        ''' Return a fake url. '''
        return 'http://wiki'


class TeamSpiritTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the ARTstability metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__wiki = FakeWiki()
        self.__team = domain.Team(metric_source_ids={self.__wiki: 'team'})
        self.__project = domain.Project(metric_sources={metric_source.Wiki:
                                                        self.__wiki})
        self.__metric = metric.TeamSpirit(subject=self.__team, 
                                          project=self.__project)

    def test_value(self):
        ''' Test that the value of the metric equals the team spirit reported
            by the wiki. '''
        self.assertEqual(self.__wiki.team_spirit('team'),
                         self.__metric.value())

    def test_numerical_value(self):
        ''' Test that the smiley is translated into an integer. '''
        self.assertEqual(2, self.__metric.numerical_value())

    def test_y_axis_range(self):
        ''' Test that the y axis range is 0-2. '''
        self.assertEqual((0, 2), self.__metric.y_axis_range())

    def test_status(self):
        ''' Test that the status is perfect. '''
        self.assertEqual('perfect', self.__metric.status())

    def test_url(self):
        ''' Test that the metric url uses the wiki url. '''
        self.assertEqual(dict(Wiki=FakeWiki().url()), self.__metric.url())

    def test_can_be_measured(self):
        ''' Test that the metric can be measured if the project has a Wiki. '''
        self.assertTrue(metric.TeamSpirit.can_be_measured(self.__team,
                                                          self.__project))

    def test_cant_be_measured_without_wiki(self):
        ''' Test that the metric cannot be measured without a Wiki. '''
        project = domain.Project()
        self.assertFalse(metric.TeamSpirit.can_be_measured(self.__team, project))

    def test_too_old(self):
        ''' Test that the metric becomes red when too old. '''
        self.__wiki.date_of_last_measurement = datetime.datetime(2000, 1, 1)
        self.assertEqual('red', self.__metric.status())

    def test_old(self):
        ''' Test that the metric becomes yellow when old. '''
        self.__wiki.date_of_last_measurement = datetime.datetime.now() - \
            metric.TeamSpirit.old_age - datetime.timedelta(hours=1)
        self.assertEqual('yellow', self.__metric.status())

    def test_norm(self):
        ''' Test that the norm mentions measurement age. '''
        self.assertEqual('Er is geen vaste norm; de stemming wordt door de '
            'teams zelf bepaald. De teams kiezen daarbij zelf een smiley. '
            'Als de meting ouder is dan 21 dagen dagen is de status geel, '
            'ouder dan 42 dagen is rood.', self.__metric.norm())


class FakeHolidayPlanner(object):  # pylint: disable=too-few-public-methods
    ''' Fake a holiday planner. '''

    def __init__(self):
        self.period = 6

    def days(self, team):  # pylint: disable=unused-argument
        ''' Return the number of consecutive days more than one team member
            is absent. '''
        return (self.period, datetime.date.today(), 
                datetime.date.today() + datetime.timedelta(days=self.period),
                team.members())

    @staticmethod
    def url():
        ''' Return the url for the holiday planner. '''
        return 'http://planner'


class TeamAbsenceTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the team absence metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__planner = FakeHolidayPlanner()
        self.__project = domain.Project(metric_sources={
            metric_source.HolidayPlanner: self.__planner})
        self.__team = domain.Team(name='Team')
        self.__team.add_member(domain.Person(name='Piet Programmer'))
        self.__team.add_member(domain.Person(name='Derk Designer'))
        self.__metric = metric.TeamAbsence(self.__team, project=self.__project)

    def test_value(self):
        ''' Test that the value is correct. '''
        self.assertEqual(6, self.__metric.value())

    def test_report(self):
        ''' Test that the report is correct. '''
        today = datetime.date.today()
        start = today.isoformat()
        end = (today + datetime.timedelta(days=6)).isoformat()
        self.assertEqual('De langste periode dat meerdere teamleden tegelijk '
                         'gepland afwezig zijn is 6 werkdagen '
                         '(%s tot en met %s). Afwezig zijn: Derk Designer, '
                         'Piet Programmer.' % (start, end),
                         self.__metric.report())

    def test_report_without_absence(self):
        ''' Test that the report is correct when there are no absences. '''
        self.__planner.period = 0
        self.assertEqual('Er zijn geen teamleden tegelijk gepland afwezig.',
                         self.__metric.report())

    def test_url(self):
        ''' Test that the url points to the url of the holiday planner. '''
        self.assertEqual(dict(Planner=FakeHolidayPlanner.url()),
                         self.__metric.url())

    def test_can_be_measured(self):
        ''' Test that the metric can be measured when the project has a 
            holiday planner. '''
        self.assertTrue(metric.TeamAbsence.can_be_measured(self.__team,
                                                           self.__project))

    def test_cant_be_measured_without_holiday_planner(self):
        ''' Test that the metric can't be measured without a holiday 
            planner metric source. '''
        project = domain.Project()
        self.assertFalse(metric.TeamAbsence.can_be_measured(self.__team, project))

    def test_cant_be_measured_without_sufficient_team_members(self):
        ''' Test that the metric can't be measured without more than one team
            member. '''
        team = domain.Team(name='Team')
        team.add_member(domain.Person(name='Piet Programmer'))
        self.assertFalse(metric.TeamAbsence.can_be_measured(team, self.__project))

    def test_default_norm(self):
        ''' Test that the norm can be shown without instantiating the class. '''
        defaults = metric.TeamAbsence.norm_template_default_values()
        self.assertEqual('Het aantal aaneengesloten dagen dat meerdere '
            'teamleden tegelijk gepland afwezig zijn is lager dan 5 '
            'werkdagen. Meer dan 10 werkdagen is rood. Het team bestaat uit '
            '(Lijst van teamleden).',
                         metric.TeamAbsence.norm_template.format(**defaults))
