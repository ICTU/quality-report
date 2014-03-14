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

from qualitylib import metric, domain
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
    
    
class FakeSubject(object):  # pylint:disable=too-few-public-methods
    ''' Fake subject (team). ''' 
    def __str__(self):
        return 'FakeSubject'


class FailingCIJobsCommonTestsMixin(object):
    ''' Unit tests of the failing CI jobs metric that don't depend on whether
        the metric is reporting on a specific team or not. '''

    def setUp(self):  # pylint: disable=invalid-name
        ''' Create the text fixture. '''
        self._metric = metric.FailingCIJobs(subject=self.subject, 
                                            jenkins=FakeJenkins(), 
                                            history=None)
        
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

        
class FailingCIJobsTestWithoutTeam(FailingCIJobsCommonTestsMixin, 
                                   unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the failing CI jobs metric without a specific team. '''
    
    subject = None
    expected_report = '1 van de 2 CI-jobs faalt.'
        

class FailingCIJobsWithTeamTest(FailingCIJobsCommonTestsMixin, 
                                unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the failing CI jobs metric with a specific team. '''
    
    subject = FakeSubject()
    expected_report = '1 van de 2 CI-jobs waarvoor team ' \
                      'FakeSubject verantwoordelijk is faalt.'


class UnusedCIJobsCommonTestsMixin(object):
    ''' Unit tests for the unused CI jobs metric that don't depend on whether
        the metric is reporting on a specific team or not. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        ''' Create the text fixture. '''
        self._metric = metric.UnusedCIJobs(subject=self.subject, 
                                            jenkins=FakeJenkins(), 
                                            history=None)
        
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


class UnusedCIJobsTestWithoutTeam(UnusedCIJobsCommonTestsMixin, 
                                  unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the unused CI jobs metric without a specific team. '''
    
    subject = None
    expected_report = '1 van de 2 CI-jobs is ongebruikt.'
        

class UnusedCIJobsWithTeamTest(UnusedCIJobsCommonTestsMixin, 
                               unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the unused CI jobs metric with a specific team. '''
    
    subject = FakeSubject()
    expected_report = '1 van de 2 CI-jobs waarvoor team ' \
                      'FakeSubject verantwoordelijk is is ongebruikt.'

         
class ARTStabilityTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the ARTstability metric. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        self.__metric = metric.ARTStability(subject=domain.Street('a', 'b'), 
                                            jenkins=FakeJenkins(), history=None)
        
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
        ''' Test that the url equals the URL provided by Jenkins. '''
        self.assertEqual(FakeJenkins.unstable_arts_url(), self.__metric.url())
        
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


class FakeNagios(object):
    ''' Fake Nagios for testing purposes. '''
    @staticmethod
    def number_of_servers_sufficiently_available():  
        # pylint: disable=invalid-name
        ''' Fake the number of available servers. '''
        return 10
        
    @staticmethod
    def number_of_servers():
        ''' Fake the number of servers. '''
        return 12
    
    @staticmethod
    def number_of_servers_per_group():
        ''' Fake the server groups. '''
        return dict(group1=4, group2=8)
    
    @staticmethod
    def availability_url():
        ''' Fake the Nagios url. '''
        return 'http://nagios'
        
        
class ServerAvailabilityTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the server availability metric. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        self.__metric = metric.ServerAvailability(subject=FakeSubject(), 
                                                  nagios=FakeNagios(),
                                                  history=None)
        
    def test_value(self):
        ''' Test that the availability is reported correctly. '''
        self.assertEqual(83., self.__metric.value())

    def test_report(self):
        ''' Test that the report is correct. '''
        self.assertEqual('Servers met voldoende beschikbaarheid is 83% ' \
                         '(10 van 12). Aantal servers per groep: group1: 4, ' \
                         'group2: 8.', self.__metric.report())

    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(dict(Nagios='http://nagios'), self.__metric.url())
        
        
class AssignedCIJobsTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the assigned CI jobs metric. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        self.__metric = metric.AssignedCIJobs(subject=FakeSubject(), 
                                              jenkins=FakeJenkins(),
                                              history=None)
        
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
