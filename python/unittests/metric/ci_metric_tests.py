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

    @classmethod
    def unstable_arts_url(cls, *args, **kwargs):
        ''' Return the urls for the unstable ARTs. '''
        return cls.UNSTABLE_ARTS_URL

    @classmethod
    def unused_jobs_url(cls, *args):
        ''' Return the url(s) of the unused job(s). '''
        return {'job_name (300 dagen)': 'http://jenkins/job_name'}


class FailingCIJobsTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the failing CI jobs metric. '''

    expected_report = '1 van de 2 CI-jobs faalt.'

    def setUp(self):  # pylint: disable=invalid-name
        ''' Create the text fixture. '''
        self._subject = None
        self._project = domain.Project(metric_sources={metric_source.Jenkins:
                                                       FakeJenkins()})
        self._metric = metric.FailingCIJobs(subject=self._subject,
                                            project=self._project)

    def test_can_be_measured(self):
        ''' Test that the metric can be measured if there is a build server. '''
        self.assertTrue(metric.FailingCIJobs.\
                        can_be_measured(self._project, self._project))

    def test_cant_be_measured_without_build_server(self):
        ''' Test that the metric cannot be measured without build server. '''
        project = domain.Project()
        self.assertFalse(metric.FailingCIJobs.can_be_measured(project, project))

    def test_norm_template_default_values(self):
        ''' Test that the right values are returned to fill in the norm 
            template. '''
        self.assertTrue(metric.FailingCIJobs.norm_template % \
                    metric.FailingCIJobs.norm_template_default_values())

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


class ProjectUnusedCIJobs(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the unused CI jobs metric. '''

    expected_report = '1 van de 2 CI-jobs is ongebruikt.'

    def setUp(self):  # pylint: disable=invalid-name
        ''' Create the text fixture. '''
        self._project = domain.Project(metric_sources={metric_source.Jenkins:
                                                       FakeJenkins()})
        self._metric = metric.UnusedCIJobs(subject=self._project,
                                           project=self._project)

    def test_can_be_measured(self):
        ''' Test that the metric can be measured if there is a build server. '''
        self.assertTrue(metric.UnusedCIJobs.\
                        can_be_measured(self._project, self._project))

    def test_cant_be_measured_without_build_server(self):
        ''' Test that the metric cannot be measured without build server. '''
        project = domain.Project()
        self.assertFalse(metric.UnusedCIJobs.can_be_measured(project,
                                                               project))

    def test_norm_template_default_values(self):
        ''' Test that the right values are returned to fill in the norm 
            template. '''
        self.assertTrue(metric.UnusedCIJobs.norm_template % \
                    metric.UnusedCIJobs.norm_template_default_values())

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
