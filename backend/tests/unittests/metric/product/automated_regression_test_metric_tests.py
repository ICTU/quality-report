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


class FakeSubject(object):
    """ Provide for a fake subject. """
    def __init__(self, metric_source_ids=None):
        self.__metric_source_ids = metric_source_ids or dict()

    @staticmethod
    def name():
        """ Return the name of the subject. """
        return 'FakeSubject'

    def metric_source_id(self, the_metric_source):
        """ Return the id of the subject for the metric source. """
        return self.__metric_source_ids.get(the_metric_source)


class FakeJenkinsTestReport(domain.MetricSource):
    """ Fake a Jenkins test report instance for unit test purposes. """
    metric_source_name = metric_source.JenkinsTestReport.metric_source_name

    def __init__(self):
        self.passed = 14
        self.skipped = 0
        self._datetime = datetime.datetime.now() - datetime.timedelta(hours=36)
        super().__init__()

    # pylint: disable=unused-argument

    @staticmethod
    def failed_tests(*args):
        """ Return the number of failing tests for the job. """
        return 4

    def skipped_tests(self, *args):
        """ Return the number of skipped tests for the job. """
        return self.skipped

    def passed_tests(self, *args):
        """ Return the number of passed tests for the job. """
        return self.passed

    def datetime(self, *args):
        """ Return a fake date. """
        return self._datetime


class FailingRegressionTestsTest(unittest.TestCase):
    """ Unit tests for the failing regression tests metric. """
    def setUp(self):
        self.__jenkins = FakeJenkinsTestReport()
        self.__subject = FakeSubject(metric_source_ids={self.__jenkins: 'jenkins_job'})
        self.__project = domain.Project(metric_sources={metric_source.SystemTestReport: self.__jenkins})
        self.__metric = metric.FailingRegressionTests(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that value of the metric equals the failing tests as reported by Jenkins. """
        self.assertEqual(self.__jenkins.failed_tests('jenkins_job') + self.__jenkins.skipped_tests('jenkins_job'),
                         self.__metric.value())

    def test_value_multiple_jobs(self):
        """ Test that the value of the metric equals to total number of failing tests if there are multiple
            test reports. """
        subject = FakeSubject(metric_source_ids={self.__jenkins: ['a', 'b']})
        failing_tests = metric.FailingRegressionTests(subject=subject, project=self.__project)
        expected = self.__jenkins.failed_tests('a', 'b') + self.__jenkins.skipped_tests('a', 'b')
        self.assertEqual(expected, failing_tests.value())

    def test_value_when_missing(self):
        """ Test that the value is negative when the test report is missing. """
        self.__jenkins.passed = -1
        self.assertTrue(self.__metric.value() < 0)

    def test_report(self):
        """ Test that the report for the metric is correct. """
        self.assertEqual('4 van de 18 regressietesten van FakeSubject slagen niet.', self.__metric.report())

    def test_report_with_skipped_tests(self):
        """ Test that the report for the metric is correct when tests are skipped. """
        self.__jenkins.skipped = 2
        self.assertEqual('6 van de 20 regressietesten van FakeSubject slagen niet. '
                         '2 van de 20 regressietesten zijn overgeslagen.', self.__metric.report())

    def test_missing_metric_source(self):
        """ Test the metric without a metric source. """
        failing_tests = metric.FailingRegressionTests(subject=domain.Product(), project=self.__project)
        self.assertTrue(failing_tests._missing())
        self.assertEqual('?', failing_tests._parameters()['tests'])


class RegressionTestAgeTest(unittest.TestCase):
    """ Unit tests for the regression test age metric. """
    def setUp(self):
        self.__jenkins = FakeJenkinsTestReport()
        self.__subject = FakeSubject(metric_source_ids={self.__jenkins: 'jenkins_job'})
        self.__project = domain.Project(metric_sources={metric_source.SystemTestReport: self.__jenkins})
        self.__metric = metric.RegressionTestAge(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that value of the metric equals the report date as reported by Jenkins. """
        expected = (datetime.datetime.now() - self.__jenkins.datetime('jenkins_job')).days
        self.assertEqual(expected, self.__metric.value())

    def test_value_multiple_jobs(self):
        """ Test that the value of the metric equals to minimum report age if there are multiple test reports. """
        subject = FakeSubject(metric_source_ids={self.__jenkins: ['a', 'b']})
        age = metric.RegressionTestAge(subject=subject, project=self.__project)
        expected = (datetime.datetime.now() - self.__jenkins.datetime('a', 'b')).days
        self.assertEqual(expected, age.value())

    def test_value_when_missing(self):
        """ Test that the value is negative when the test report is missing. """
        self.__jenkins._datetime = datetime.datetime.min
        self.assertTrue(self.__metric.value() < 0)

    def test_report(self):
        """ Test that the report for the metric is correct. """
        days = (datetime.datetime.now() - self.__jenkins.datetime()).days
        self.assertEqual('De regressietest van FakeSubject is {0} dagen geleden gedraaid.'.format(days),
                         self.__metric.report())
