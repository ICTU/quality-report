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

import unittest

from typing import Type

from hqlib import metric, domain, metric_source
from hqlib.metric.product.alerts_metrics import AlertsMetric


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


class FakeJenkinsOWASPDependenciesReport(domain.MetricSource):
    """ Fake a Jenkins OWASP dependency report for unit test purposes. """

    metric_source_name = metric_source.JenkinsOWASPDependencyReport.metric_source_name

    @staticmethod
    def nr_warnings(job_names, priority):
        """ Return the number of warnings for the jobs. """
        return -1 if job_names == [None] else dict(high=4, normal=2, low=14)[priority]


class HighPriorityOWASPDependencyWarningsTest(unittest.TestCase):
    """ Unit tests for the high priority OWASP dependency warnings metric. """

    class_under_test: Type[AlertsMetric] = metric.HighPriorityOWASPDependencyWarnings  # May be overridden

    def setUp(self):
        self.__jenkins = FakeJenkinsOWASPDependenciesReport()
        self.__subject = FakeSubject(metric_source_ids={self.__jenkins: 'jenkins_job'})
        self.__project = domain.Project(metric_sources={metric_source.OWASPDependencyReport: self.__jenkins})
        self.__metric = self.class_under_test(subject=self.__subject, project=self.__project)

    def expected_warnings(self, job):
        """ Return the number of expected warnings. """
        return self.__jenkins.nr_warnings(job, self.class_under_test.risk_level_key)

    def test_value(self):
        """ Test that value of the metric equals the number of warnings as reported by Jenkins. """
        self.assertEqual(self.expected_warnings('jenkins_job'), self.__metric.value())

    def test_value_multiple_jobs(self):
        """ Test that the value of the metric equals the number of warnings if there are multiple
            test reports. """
        subject = FakeSubject(metric_source_ids={self.__jenkins: ['a', 'b']})
        failing_tests = self.class_under_test(subject=subject, project=self.__project)
        self.assertEqual(self.expected_warnings(['a', 'b']), failing_tests.value())

    def test_value_without_metric_source(self):
        """ Test that the value is -1 when no OWASP dependency report is provided. """
        owasp = self.class_under_test(subject=self.__subject, project=domain.Project())
        self.assertEqual(-1, owasp.value())

    def test_report(self):
        """ Test that the report for the metric is correct. """
        expected_report = 'Dependencies van FakeSubject hebben {0} {1} prioriteit waarschuwingen.'.format(
            self.expected_warnings('jenkins_job'), self.class_under_test.risk_level)
        self.assertEqual(expected_report, self.__metric.report())

    def test_norm(self):
        """ Test that the norm is correct. """
        expected_norm = 'Dependencies van het product hebben geen {} prioriteit OWASP waarschuwingen. ' \
                        'Meer dan {} is rood.'.format(self.class_under_test.risk_level,
                                                      self.class_under_test.low_target_value)
        self.assertEqual(expected_norm,
                         self.__metric.norm_template.format(**self.__metric.norm_template_default_values()))

    def test_is_missing_without_jenkins(self):
        """ Test that metric is missing when Jenkins is not available. """
        owasp = self.class_under_test(self.__subject, domain.Project())
        self.assertTrue(owasp._missing())  # pylint: disable=protected-access

    def test_is_missing_without_jenkins_job(self):
        """ Test that the metric cannot be measured without Jenkins. """
        owasp = self.class_under_test(FakeSubject(), self.__project)
        self.assertTrue(owasp._missing())  # pylint: disable=protected-access

    def test_is_not_missing(self):
        """ Test that the metric is not missing when Jenkins is available. """
        self.assertFalse(self.__metric._missing())  # pylint: disable=protected-access


class NormalPriorityOWASPDependencyWarningsTest(HighPriorityOWASPDependencyWarningsTest):
    """ Unit tests for the normal priority OWASP dependency warnings metric. """

    class_under_test = metric.NormalPriorityOWASPDependencyWarnings
