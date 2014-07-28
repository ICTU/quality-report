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
import unittest


class FakeJenkins(object):
    ''' Fake Jenkins instance for testing purposes. '''
    # pylint: disable=unused-argument

    UNSTABLE_ARTS_URL = {}

    @classmethod
    def failing_jobs_url(cls, *args):
        ''' Return the url(s) of the failing job(s). '''
        return {'job_name (3 dagen)': 'http://jenkins/job_name'}

    @staticmethod
    def number_of_jobs(*args):
        ''' Return the total number of CI jobs. '''
        return 2

    @staticmethod
    def number_of_assigned_jobs():
        ''' Return the number of jobs assigned to a team. '''
        return 2

    @classmethod
    def unstable_arts_url(cls, *args, **kwargs):
        ''' Return the urls for the unstable ARTs. '''
        return cls.UNSTABLE_ARTS_URL

    @staticmethod
    def unassigned_jobs_url():
        ''' Return the urls for the unassigned jobs. '''
        return dict(job='http://job')

    @classmethod
    def unused_jobs_url(cls, *args):
        ''' Return the url(s) of the unused job(s). '''
        return {'job_name (300 dagen)': 'http://jenkins/job_name'}


class FailingCIJobsCommonTestsMixin(object):
    ''' Unit tests of the failing CI jobs metric that don't depend on whether
        the metric is reporting on a specific team or not. '''

    def test_value(self):
        ''' Test that the value equals the number of failing jobs. '''
        self.assertEqual(1, self._metric.value())

    def test_url(self):
        ''' Test that the url of the metric equals the url of Jenkins. '''
        self.assertEqual(FakeJenkins().failing_jobs_url(), self._metric.url())

    def test_report(self):
        ''' Test the metric report. '''
        self.assertEqual(self.expected_report, self._metric.report())

    def test_label(self):
        ''' Test that the label to use in the HTML report is correct. '''
        self.assertEqual('Falende jobs', self._metric.url_label())


class ProjectFailingCIJobsTest(FailingCIJobsCommonTestsMixin, 
                               unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the failing CI jobs metric without a specific team. '''

    expected_report = '1 van de 2 CI-jobs faalt.'

    def setUp(self):  # pylint: disable=invalid-name
        ''' Create the text fixture. '''
        self._subject = None
        self._project = domain.Project(metric_sources={metric_source.Jenkins:
                                                       FakeJenkins()})
        self._metric = metric.ProjectFailingCIJobs(subject=self._subject,
                                                   project=self._project)

    def test_can_be_measured(self):
        ''' Test that the metric can be measured if there is a build server. '''
        self.failUnless(metric.ProjectFailingCIJobs.\
                        can_be_measured(self._project, self._project))

    def test_cant_be_measured_without_build_server(self):
        ''' Test that the metric cannot be measured without build server. '''
        project = domain.Project()
        for index in range(2):
            team = domain.Team(name='Team %d' % index)
            project.add_team(team, responsible=True)
        self.failIf(metric.ProjectFailingCIJobs.can_be_measured(team, project))

    def test_norm_template_default_values(self):
        ''' Test that the right values are returned to fill in the norm 
            template. '''
        self.failUnless(metric.ProjectFailingCIJobs.norm_template % \
                    metric.ProjectFailingCIJobs.norm_template_default_values())


class TeamFailingCIJobsTest(FailingCIJobsCommonTestsMixin, unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the failing CI jobs metric with a specific team. '''

    expected_report = '1 van de 2 CI-jobs waarvoor team ' \
                      'Team verantwoordelijk is faalt.'

    def setUp(self):  # pylint: disable=invalid-name
        ''' Create the text fixture. '''
        self._project = domain.Project(metric_sources={metric_source.Jenkins:
                                                       FakeJenkins()})
        self._subject = domain.Team(name='Team')
        self._project.add_team(self._subject, responsible=True)
        self._project.add_team(domain.Team(name='Another team'),
                               responsible=True)
        self._metric = metric.TeamFailingCIJobs(subject=self._subject, 
                                                project=self._project)

    def test_can_be_measured(self):
        ''' Test that the metric can be measured when the project has 
            multiple teams. '''
        self.failUnless(metric.TeamFailingCIJobs.can_be_measured(self._subject, 
                                                                 self._project))

    def test_wont_be_measured_unless_multiple_teams(self):
        ''' Test that the metric won't be measured unless the project has 
            multiple teams. '''
        project = domain.Project(metric_sources={metric_source.Jenkins:
                                                 FakeJenkins()})
        team = domain.Team(name='Single team')
        project.add_team(team, responsible=True)
        self.failIf(metric.TeamFailingCIJobs.can_be_measured(team, project))

    def test_cant_be_measured_without_build_server(self):
        ''' Test that the metric cannot be measured without build server. '''
        project = domain.Project()
        for index in range(2):
            team = domain.Team(name='Team %d' % index)
            project.add_team(team, responsible=True)
        self.failIf(metric.TeamFailingCIJobs.can_be_measured(team, project))

    def test_norm_template_default_values(self):
        ''' Test that the right values are returned to fill in the norm 
            template. '''
        self.failUnless(metric.TeamFailingCIJobs.norm_template % \
                        metric.TeamFailingCIJobs.norm_template_default_values())


class UnusedCIJobsCommonTestsMixin(object):
    ''' Unit tests for the unused CI jobs metric that don't depend on whether
        the metric is reporting on a specific team or not. '''

    def test_value(self):
        ''' Test that the value equals the number of failing jobs. '''
        self.assertEqual(1, self._metric.value())

    def test_url(self):
        ''' Test that the url of the metric equals the url of Jenkins. '''
        self.assertEqual(FakeJenkins().unused_jobs_url(), self._metric.url())

    def test_report(self):
        ''' Test the metric report. '''
        self.assertEqual(self.expected_report, self._metric.report())

    def test_label(self):
        ''' Test that the label to use in the HTML report is correct. '''
        self.assertEqual('Ongebruikte jobs', self._metric.url_label())


class TeamUnusedCIJobsTest(UnusedCIJobsCommonTestsMixin, unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the unused CI jobs metric with a specific team. '''

    expected_report = '1 van de 2 CI-jobs waarvoor team ' \
                      'Team verantwoordelijk is is ongebruikt.'

    def setUp(self):  # pylint: disable=invalid-name
        ''' Create the text fixture. '''
        self._project = domain.Project(metric_sources={metric_source.Jenkins: 
                                                       FakeJenkins()})
        self.__team = domain.Team(name='Team')
        self._project.add_team(self.__team)
        self._project.add_team(domain.Team(name='Another team'))
        self._metric = metric.TeamUnusedCIJobs(subject=self.__team,
                                               project=self._project)

    def test_can_be_measured(self):
        ''' Test that the metric can be measured when the project as multiple
            teams. '''
        self.failUnless(metric.TeamUnusedCIJobs.can_be_measured(self.__team,
                                                                self._project))

    def test_wont_be_measured_unless_multiple_teams(self):
        ''' Test that the metric won't be measured unless the project has
            multiple teams. '''
        project = domain.Project(metric_sources={metric_source.Jenkins: 
                                                 FakeJenkins()})
        project.add_team(self.__team)
        self.failIf(metric.TeamUnusedCIJobs.can_be_measured(self.__team, 
                                                            project))

    def test_cant_be_measured_without_build_server(self):
        ''' Test that the metric cannot be measured without build server. '''
        project = domain.Project()
        project.add_team(self.__team)
        project.add_team(domain.Team(name='Another team'))
        self.failIf(metric.TeamUnusedCIJobs.can_be_measured(self.__team, 
                                                            project))

    def test_norm_template_default_values(self):
        ''' Test that the right values are returned to fill in the norm 
            template. '''
        self.failUnless(metric.TeamUnusedCIJobs.norm_template % \
                    metric.TeamUnusedCIJobs.norm_template_default_values())


class ProjectUnusedCIJobs(UnusedCIJobsCommonTestsMixin, unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the unused CI jobs metric without a specific team. '''

    expected_report = '1 van de 2 CI-jobs is ongebruikt.'

    def setUp(self):  # pylint: disable=invalid-name
        ''' Create the text fixture. '''
        self._project = domain.Project(metric_sources={metric_source.Jenkins:
                                                       FakeJenkins()})
        self._metric = metric.ProjectUnusedCIJobs(subject=self._project,
                                                  project=self._project)

    def test_can_be_measured(self):
        ''' Test that the metric can be measured if there is a build server. '''
        self.failUnless(metric.ProjectUnusedCIJobs.\
                        can_be_measured(self._project, self._project))

    def test_cant_be_measured_without_build_server(self):
        ''' Test that the metric cannot be measured without build server. '''
        project = domain.Project()
        self.failIf(metric.ProjectUnusedCIJobs.can_be_measured(project, 
                                                               project))

    def test_norm_template_default_values(self):
        ''' Test that the right values are returned to fill in the norm 
            template. '''
        self.failUnless(metric.ProjectUnusedCIJobs.norm_template % \
                    metric.ProjectUnusedCIJobs.norm_template_default_values())


class ARTStabilityTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the ARTstability metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__project = domain.Project(metric_sources={metric_source.Jenkins: 
                                                        FakeJenkins()})
        self.__street = domain.Street('b', name='a', url='http://street')
        self.__metric = metric.ARTStability(subject=self.__street,
                                            project=self.__project)

    def test_value_stable(self):
        ''' Test that the value of the metric equals the list of unstable ARTs
            return by Jenkins. '''
        FakeJenkins.UNSTABLE_ARTS_URL = {}
        self.assertEqual(0, self.__metric.value())

    def test_report_stable(self):
        ''' Test that the report is correct. '''
        FakeJenkins.UNSTABLE_ARTS_URL = {}
        self.assertEqual('Alle ARTs hebben de afgelopen 3 dagen succesvol ' \
                         'gedraaid in de "a"-straat.', self.__metric.report())

    def test_value_unstable(self):
        ''' Test that the value of the metric equals the list of unstable ARTs
            return by Jenkins. '''
        FakeJenkins.UNSTABLE_ARTS_URL = {'unstable_art': 'http://url'}
        self.assertEqual(1, self.__metric.value())

    def test_report_unstable(self):
        ''' Test that the report is correct. '''
        FakeJenkins.UNSTABLE_ARTS_URL = {'unstable_art': 'http://url'}
        self.assertEqual('1 ARTs hebben de afgelopen 3 dagen ' \
                         'niet succesvol gedraaid in de "a"-straat.', 
                         self.__metric.report())

    def test_url(self):
        ''' Test that the url equals the URL provided by Jenkins and the url
            of the street. '''
        expected_urls = dict()
        expected_urls.update(FakeJenkins.unstable_arts_url())
        street_label = '"%s"-straat' % self.__street.name()
        expected_urls[street_label] = self.__street.url()
        self.assertEqual(expected_urls, self.__metric.url())

    def test_url_without_street(self):
        ''' Test the url without a street url. '''
        expected_urls = dict()
        expected_urls.update(FakeJenkins.unstable_arts_url())
        street = domain.Street('b', name='a')
        art_stability = metric.ARTStability(subject=street,
                                            project=self.__project)
        self.assertEqual(expected_urls, art_stability.url())

    def test_numerical_value(self):
        ''' Test that the numerical value is the number of unstable ARTs. '''
        FakeJenkins.UNSTABLE_ARTS_URL = {'unstable_art': 'http://url'}
        self.assertEqual(1, self.__metric.numerical_value())

    def test_status_stable(self):
        ''' Test that the status is green when the number of unstable 
            ARTs is zero. '''
        FakeJenkins.UNSTABLE_ARTS_URL = {}
        self.assertEqual('perfect', self.__metric.status())

    def test_status_unstable(self):
        ''' Test that the status is red when the number of unstable ARTs is
            not zero. '''
        FakeJenkins.UNSTABLE_ARTS_URL = {'unstable_art': 'http://url', 
                                         'unstable_art2': 'http://url'}
        self.assertEqual('red', self.__metric.status())


class AssignedCIJobsTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the assigned CI jobs metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__project = domain.Project(metric_sources={metric_source.Jenkins:
                                                        FakeJenkins()})
        self.__project.add_team('team1')
        self.__project.add_team('team2')
        self.__metric = metric.AssignedCIJobs(subject=domain.Team(name='Team'), 
                                              project=self.__project)

    def test_value(self):
        ''' Test that the availability is reported correctly. '''
        self.assertEqual(100., self.__metric.value())

    def test_report(self):
        ''' Test that the report is correct. '''
        self.assertEqual('100% (2 van 2) van de CI-jobs is toegewezen aan ' \
                         'een team.', self.__metric.report())

    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(FakeJenkins().unassigned_jobs_url(), 
                         self.__metric.url())

    def test_label(self):
        ''' Test that the label is correct. '''
        self.assertEqual('Niet toegewezen jobs', self.__metric.url_label())

    def test_can_be_measured(self):
        ''' Test that the metric can be measured when the project has a build 
            server and the project has more than one team. '''
        self.failUnless(metric.AssignedCIJobs.can_be_measured(self.__project, 
                                                              self.__project))

    def test_cant_be_measured_without_build_server(self):
        ''' Test that the metric can be measured when the project has a build 
            server and the project has more than one team. '''
        project = domain.Project()
        self.failIf(metric.AssignedCIJobs.can_be_measured(self.__project, 
                                                          project))

    def test_cant_be_measured_without_multiple_teams(self):
        ''' Test that the metric can be measured when the project has a build 
            server and the project has more than one team. '''
        project = domain.Project(metric_sources={metric_source.Jenkins:
                                                 FakeJenkins()})
        self.failIf(metric.AssignedCIJobs.can_be_measured(project, project))
