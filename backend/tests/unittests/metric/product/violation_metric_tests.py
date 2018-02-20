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

from hqlib import metric, domain, metric_source


class FakeSonar(object):
    """ Provide for a fake Sonar object so that the unit test don't need access to an actual Sonar instance. """
    # pylint: disable=unused-argument

    metric_source_name = metric_source.Sonar.metric_source_name

    def __init__(self, blocker_violations=0, critical_violations=0, major_violations=0):
        self.__blocker_violations = blocker_violations
        self.__critical_violations = critical_violations
        self.__major_violations = major_violations

    def blocker_violations(self, *args):
        """ Return the number of blocker violations. """
        return self.__blocker_violations

    def critical_violations(self, *args):
        """ Return the number of critical violations. """
        return self.__critical_violations

    def major_violations(self, *args):
        """ Return the number of major violations. """
        return self.__major_violations

    @staticmethod
    def false_positives(*args):
        """ Return the number of issues marked as false positive. """
        return 3


class ViolationsTestMixin(object):
    """ Unit tests for the Violations metric classes. """

    def setUp(self):  # pylint: disable=invalid-name,missing-docstring
        self.__nr_violations = 51
        self.__sonar = FakeSonar(blocker_violations=self.__nr_violations,
                                 critical_violations=self.__nr_violations,
                                 major_violations=self.__nr_violations)
        project = domain.Project(metric_sources={metric_source.Sonar: self.__sonar})
        self.__subject = domain.Product(short_name='PR', name='FakeSubject',
                                        metric_source_ids={self.__sonar: "sonar id"})
        self._metric = self.metric_class(subject=self.__subject, project=project)

    def test_numerical_value(self):
        """ Test that the numerical value of the metric equals the number of violation as provided by Sonar. """
        self.assertEqual(self.__nr_violations, self._metric.numerical_value())

    def test_value(self):
        """ Test that the value is equal to the number of violations as reported by Sonar. """
        self.assertEqual(self.__nr_violations, self._metric.value())

    def test_status(self):
        """ Test that the status is red when there are too many violations. """
        self.assertEqual('red', self._metric.status())

    def test_status_with_technical_debt(self):
        """ Test that the status is grey when the subject has accepted technical debt. """
        self.__subject.technical_debt_target = lambda *args: domain.TechnicalDebtTarget(51, 'Comment')
        self.assertEqual('grey', self._metric.status())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual('FakeSubject heeft {nr} {type} violations.'.format(nr=self.__nr_violations,
                                                                            type=self.violation_type),
                         self._metric.report())

    def test_is_perfect(self):
        """ Test that the metric is perfect when the number of violations is zero. """
        sonar = FakeSonar()
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        product = domain.Product(metric_source_ids={sonar: "sonar id"})
        violations = self.metric_class(subject=product, project=project)
        self.assertEqual('perfect', violations.status())

    def test_norm_template_default_values(self):
        """ Test that the right values are returned to fill in the norm template. """
        self.assertTrue(self.metric_class.norm_template % self.metric_class.norm_template_default_values())


class BlockerViolationsTest(ViolationsTestMixin, unittest.TestCase):
    """ Unit tests for the BlockerViolations metric class. """

    metric_class = metric.BlockerViolations
    violation_type = 'blocker'


class CriticalViolationsTest(ViolationsTestMixin, unittest.TestCase):
    """ Unit tests for the CriticalViolations metric class. """

    metric_class = metric.CriticalViolations
    violation_type = 'critical'


class MajorViolationsTest(ViolationsTestMixin, unittest.TestCase):
    """ Unit tests for the MajorViolations metric class. """

    metric_class = metric.MajorViolations
    violation_type = 'major'


class FalsePositivesTest(unittest.TestCase):
    """ Unit tests for the false positives metric class. """

    def setUp(self):
        sonar = FakeSonar()
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        self.__subject = domain.Product(short_name='PR', name='FakeSubject', metric_source_ids={sonar: "sonar id"})
        self.__metric = metric.FalsePositives(subject=self.__subject, project=project)

    def test_value(self):
        """ Test that the value is equal to the number of false positives as reported by Sonar. """
        self.assertEqual(3, self.__metric.value())
