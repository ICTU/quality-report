'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

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


class FakeSubject(object):  # pylint:disable=too-few-public-methods
    ''' Fake subject (team). '''
    @staticmethod
    def name():
        ''' Return product name. '''
        return 'FakeSubject'


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
        self.failUnless(metric.TeamProgress.can_be_measured(self.__team,
                                                            self.__project))

    def test_can_only_be_measured_for_scrum_teams(self):
        ''' Test that the metric cannot be measured if the team is not a Scrum
            team. '''
        team = domain.Team(name='ABC', metric_source_ids={self.__birt: 'abc'})
        self.failIf(metric.TeamProgress.can_be_measured(team, self.__project))

    def test_cant_be_measured_without_birt_id(self):
        ''' Test that the metric cannot be measured if the team has no Birt 
            id. '''
        team = domain.Team(name='Team', is_scrum_team=True)
        self.failIf(metric.TeamProgress.can_be_measured(team, self.__project))

    def test_cant_be_measured_without_birt(self):
        ''' Test that the metric cannot be measured without Birt. '''
        project = domain.Project()
        self.failIf(metric.TeamProgress.can_be_measured(self.__team, project))

    def test_norm_template_default_values(self):
        ''' Test that the right values are returned to fill in the norm 
            template. '''
        self.failUnless(metric.TeamProgress.norm_template % \
                        metric.TeamProgress.norm_template_default_values())


class FakeWiki(object):
    ''' Fake a wiki metric source. '''
    @staticmethod  # pylint: disable=unused-argument
    def team_spirit(*args):
        ''' Return a fake team spirit. '''
        return ':-)'

    @staticmethod  # pylint: disable=unused-argument
    def date_of_last_team_spirit_measurement(*args):  
        # pylint: disable=invalid-name
        ''' Return a fake date. '''
        return datetime.datetime.now()

    @staticmethod
    def url():
        ''' Return a fake url. '''
        return 'http://wiki'


class TeamSpiritTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the ARTstability metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__team = FakeSubject()
        self.__wiki = FakeWiki()
        self.__project = domain.Project(metric_sources={metric_source.Wiki:
                                                        self.__wiki})
        self.__metric = metric.TeamSpirit(subject=self.__team, 
                                          project=self.__project)

    def test_value(self):
        ''' Test that the value of the metric equals the team spirit reported
            by the wiki. '''
        self.assertEqual(self.__wiki.team_spirit(FakeSubject()),
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
        self.failUnless(metric.TeamSpirit.can_be_measured(self.__team,
                                                          self.__project))

    def test_cant_be_measured_without_wiki(self):
        ''' Test that the metric cannot be measured without a Wiki. '''
        project = domain.Project()
        self.failIf(metric.TeamSpirit.can_be_measured(self.__team, project))


class ReleaseAgeTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the release age metric. '''

    class FakeArchive(object):
        ''' Fake a release archive. '''
        @staticmethod
        def date_of_most_recent_file():
            ''' Return the date of the most recent file in the archive. '''
            return datetime.datetime.now() - datetime.timedelta(minutes=1)

        @staticmethod
        def url():
            ''' Return a fake url. '''
            return 'http://archive'

        @staticmethod
        def name():
            ''' Return a fake name. '''
            return 'ABC'

    def setUp(self):  # pylint: disable=invalid-name
        project = domain.Project()
        team = domain.Team(name='Team', 
                           release_archives=[ReleaseAgeTest.FakeArchive()])
        self.__metric = metric.ReleaseAge(team, project=project)

    def test_value(self):
        ''' Test that the value is correct. '''
        self.assertEqual(0, self.__metric.value())

    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual({'Release-archief ABC': 'http://archive'}, 
                         self.__metric.url())

    def test_report(self):
        ''' Test that the report is correct. '''
        self.assertEqual('Release leeftijden: ABC is 0 dag(en) oud.', 
                         self.__metric.report())

    def test_can_be_measured(self):
        ''' Test that the metric can be measured if the team has release
            archives. '''
        team = domain.Team(name='Team', release_archives=['Archive'])
        project = domain.Project()
        self.failUnless(metric.ReleaseAge.can_be_measured(team, project))

    def test_cant_be_measured_without_release_archive(self):
        ''' Test that the metric cannot be measured if the team has no
            release archives. '''
        team = domain.Team(name='Team')
        project = domain.Project()
        self.failIf(metric.ReleaseAge.can_be_measured(team, project))
