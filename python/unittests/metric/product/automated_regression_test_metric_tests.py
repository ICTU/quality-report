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

import datetime
import unittest
from qualitylib import metric, domain, metric_source


class FakeEmma(object):
    ''' Fake Emma. '''
    url = 'http://emma'

    @staticmethod
    def coverage(emma_id):  # pylint: disable=unused-argument
        ''' Return the ART coverage. '''
        return 98

    @classmethod
    def get_coverage_url(cls, emma_id):  # pylint: disable=unused-argument
        ''' Return a fake url. '''
        return cls.url

    @staticmethod
    def coverage_date(emma_id):  # pylint: disable=unused-argument
        ''' Return a fake date. '''
        return datetime.datetime.today() - datetime.timedelta(days=4)


class FakeJaCoCo(FakeEmma):
    ''' Fake JaCoCo. '''
    url = 'http://jacoco'


class FakeSubject(object):
    ''' Provide for a fake subject. '''
    def __init__(self, version='', art='', metric_source_ids=None):
        self.__version = version
        self.__art = art
        self.__metric_source_ids = metric_source_ids or dict()

    @staticmethod
    def name():
        ''' Return the name of the subject. '''
        return 'FakeSubject'

    def product_version(self):
        ''' Return the version of the subject. '''
        return self.__version

    def metric_source_id(self, the_metric_source):
        ''' Return the id of the subject for the metric source. '''
        return self.__metric_source_ids.get(the_metric_source, None)


class ARTCoverageJacocoTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the ART coverage metric. '''
    def setUp(self):  # pylint: disable=invalid-name
        self.__jacoco = FakeJaCoCo()
        self.__subject = FakeSubject(
            metric_source_ids={self.__jacoco: 'jacoco_id'}, version='1.1')
        self.__project = domain.Project(metric_sources={metric_source.JaCoCo:
                                                        self.__jacoco})
        self.__metric = metric.ARTCoverage(subject=self.__subject, 
                                           project=self.__project)

    def test_value(self):
        ''' Test that value of the metric equals the coverage as reported by
            Jacoco. '''
        self.assertEqual(self.__jacoco.coverage(None), self.__metric.value())

    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(dict(JaCoCo='http://jacoco'), self.__metric.url())

    def test_report(self):
        ''' Test that the report is correct. '''
        self.failUnless(self.__metric.report().startswith('FakeSubject ART ' \
                                                          'coverage is 98%'))

    def test_can_be_measured(self):
        ''' Test that the metric can be measured if the project has Jacoco and
            the product has a Jacoco id. '''
        self.failUnless(metric.ARTCoverage.can_be_measured(self.__subject,
                                                           self.__project))

    def test_cant_be_measured_without_jacoco(self):
        ''' Test that the metric can not be measured without Jacoco. '''
        project = domain.Project()
        self.failIf(metric.ARTCoverage.can_be_measured(self.__subject, project))

    def test_cant_be_measured_without_jacoco_id(self):
        ''' Test that the metric can not be measured if the product has no 
            Jacoco id. '''
        subject = FakeSubject(version='1.1')
        self.failIf(metric.ARTCoverage.can_be_measured(subject, self.__project))


class ARTCoverageEmmaTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the ART coverage metric. '''
    def setUp(self):  # pylint: disable=invalid-name
        self.__emma = FakeEmma()
        self.__subject = FakeSubject(metric_source_ids={self.__emma: 'emma_id'})
        self.__project = domain.Project(metric_sources={metric_source.Emma:
                                                        self.__emma})
        self.__metric = metric.ARTCoverage(subject=self.__subject, 
                                           project=self.__project)

    def test_value(self):
        ''' Test that value of the metric equals the coverage as reported by
            Emma. '''
        self.assertEqual(self.__emma.coverage(None), self.__metric.value())

    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(dict(Emma='http://emma'), self.__metric.url())

    def test_report(self):
        ''' Test that the report is correct. '''
        self.failUnless(self.__metric.report().startswith('FakeSubject ART ' \
                                                          'coverage is 98%'))

    def test_can_be_measured(self):
        ''' Test that the metric can be measured if the project has Emma and
            the product has an Emma id. '''
        self.failUnless(metric.ARTCoverage.can_be_measured(self.__subject,
                                                           self.__project))

    def test_cant_be_measured_without_jacoco(self):
        ''' Test that the metric can not be measured without Emma. '''
        project = domain.Project()
        self.failIf(metric.ARTCoverage.can_be_measured(self.__subject, project))

    def test_cant_be_measured_without_jacoco_id(self):
        ''' Test that the metric can not be measured if the product has no 
            Emma id. '''
        subject = FakeSubject(version='1.1')
        self.failIf(metric.ARTCoverage.can_be_measured(subject, self.__project))


class FakeBirt(object):
    ''' Fake a Birt instance. '''
    @classmethod
    def has_art_performance(cls, product, version):
        # pylint: disable=unused-argument
        ''' Return whether Birt can report on the relative ART performance for
            this product and version. '''
        return True

    @staticmethod
    def nr_slower_pages_art(product, version):
        ''' Return the number of slow pages. '''
        # pylint: disable=unused-argument
        return 10

    @staticmethod
    def relative_art_performance_url(product):
        ''' Return the url for the relative art performance report. '''
        return 'http://birt/performance/%s/' % product


class RelativeARTPerformanceTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the ART coverage metric. '''
    def setUp(self):  # pylint: disable=invalid-name
        self.__birt = FakeBirt()
        self.__subject = FakeSubject(version='1',
                                     metric_source_ids={self.__birt: 'birt_id'})
        self.__project = domain.Project(metric_sources={metric_source.Birt:
                                                        self.__birt})
        self.__metric = metric.RelativeARTPerformance(subject=self.__subject,
                                                      project=self.__project)

    def test_value(self):
        ''' Test that value of the metric equals the number of pages that are
            slower as reported by Birt. '''
        self.assertEqual(10, self.__metric.value())

    def test_url(self):
        ''' Test that the url correctly points to the Birt report. '''
        self.assertEqual({'Birt':
                          self.__birt.relative_art_performance_url('birt_id')},
                         self.__metric.url())

    def test_report(self):
        ''' Test that the report for the metric is correct. '''
        self.assertEqual('10 van de paginas van FakeSubject ' \
                         'laadt langzamer bij het uitvoeren van de laatste ' \
                         'test dan bij de voorlaatste test.',
                         self.__metric.report())

    def test_cant_be_measured_without_birt(self):
        ''' Test that the metric cannot be measured without Birt. '''
        self.failIf(metric.RelativeARTPerformance.can_be_measured(
            self.__subject, domain.Project()))

    def test_can_be_measured(self):
        ''' Test that metric can be measured when Birt is available and Birt
            has relative ART performance data for the product. '''
        self.failUnless(metric.RelativeARTPerformance.can_be_measured(
            self.__subject, self.__project))


class FakeJenkinsTestReport(object):
    ''' Fake a Jenkins test report instance for unit test purposes. '''
    @staticmethod
    def failed_tests(job_name):  # pylint: disable=unused-argument
        ''' Return the number of failing tests for the job. '''
        return 4

    @staticmethod
    def skipped_tests(job_name):  # pylint: disable=unused-argument
        ''' Return the number of skipped tests for the job. '''
        return 2

    @staticmethod
    def passed_tests(job_name):  # pylint: disable=unused-argument
        ''' Return the number of passed tests for the job. '''
        return 14

    @staticmethod
    def test_report_url(job_name):
        ''' Return the url for the job. '''
        return 'http://jenkins/%s' % job_name


class FailingRegressionTestsTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the failing regression tests metric. '''
    def setUp(self):  # pylint: disable=invalid-name
        self.__jenkins = FakeJenkinsTestReport()
        self.__subject = FakeSubject(
            metric_source_ids={self.__jenkins: 'jenkins_job'})
        self.__project = domain.Project(metric_sources={
                                            metric_source.JenkinsTestReport:
                                                self.__jenkins})
        self.__metric = metric.FailingRegressionTests(subject=self.__subject, 
                                                      project=self.__project)

    def test_value(self):
        ''' Test that value of the metric equals the failing tests as reported
            by Jenkins. '''
        self.assertEqual(self.__jenkins.failed_tests('jenkins_job') + \
                         self.__jenkins.skipped_tests('jenkins_job'), 
                         self.__metric.value())

    def test_value_multiple_jobs(self):
        ''' Test that the value of the metric equals to total number of
            failing tests if there are multiple test reports. '''
        subject = FakeSubject(metric_source_ids={self.__jenkins: ['a', 'b']})
        failing_tests = metric.FailingRegressionTests(subject=subject,
                                                      project=self.__project)
        expected = self.__jenkins.failed_tests(['a', 'b']) + \
                   self.__jenkins.skipped_tests(['a', 'b'])
        self.assertEqual(expected, failing_tests.value())

    def test_report(self):
        ''' Test that the report for the metric is correct. '''
        self.assertEqual('6 van de 20 regressietesten van FakeSubject ' 
                         'slagen niet.', self.__metric.report())

    def test_url(self):
        ''' Test that the url points to the Jenkins job. '''
        self.assertEqual({'Jenkins test report': 
                          self.__jenkins.test_report_url('jenkins_job')},
                         self.__metric.url())

    def test_url_multiple_jobs(self):
        ''' Test that the url points to the Jenkins jobs. '''
        subject = FakeSubject(metric_source_ids={self.__jenkins: ['a', 'b']})
        failing_tests = metric.FailingRegressionTests(subject=subject,
                                                      project=self.__project)
        self.assertEqual({'Jenkins test report a': 
                              self.__jenkins.test_report_url('a'),
                          'Jenkins test report b':
                              self.__jenkins.test_report_url('b')},
                         failing_tests.url())

    def test_can_be_measured(self):
        ''' Test that metric can be measured when Jenkins is available and the 
            product has a Jenkins job. '''
        self.failUnless(
            metric.FailingRegressionTests.can_be_measured(self.__subject, 
                                                          self.__project))

    def test_cant_be_measured_without_jenkins(self):
        ''' Test that the metric cannot be measured without Jenkins. '''
        self.failIf(
            metric.FailingRegressionTests.can_be_measured(self.__subject, 
                                                          domain.Project()))

    def test_cant_be_measured_without_jenkins_job(self):
        ''' Test that the metric cannot be measured without Jenkins job. '''
        self.failIf(
            metric.FailingRegressionTests.can_be_measured(FakeSubject(), 
                                                          self.__project))
