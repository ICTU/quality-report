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
from unittest.mock import MagicMock
from hqlib import metric, domain, metric_source


class ViolationsTestMixin(object):
    """ Unit tests for the Violations metric classes. """

    def setUp(self):  # pylint: disable=invalid-name,missing-docstring
        self.__nr_violations = 51
        self.__sonar = MagicMock()
        self.__sonar.major_violations = MagicMock(return_value=self.__nr_violations)
        self.__sonar.critical_violations = MagicMock(return_value=self.__nr_violations)
        self.__sonar.blocker_violations = MagicMock(return_value=self.__nr_violations)

        project = domain.Project(metric_sources={metric_source.Sonar: self.__sonar})
        self.__subject = domain.Product(short_name='PR', name='FakeSubject',
                                        metric_source_ids={self.__sonar: "sonar id"})
        self._metric = self.metric_class(subject=self.__subject, project=project)

    def test_numerical_value(self):
        """ Test that the numerical value of the metric equals the number of violation as provided by Sonar. """
        self.__sonar.major_violations = MagicMock(return_value=self.__nr_violations)
        self.assertEqual(self.__nr_violations, self._metric.numerical_value())

    def test_value(self):
        """ Test that the value is equal to the number of violations as reported by Sonar. """
        self.assertEqual(self.__nr_violations, self._metric.value())

    def test_value_no_metric_source(self):
        """ Test that the value is equal to -1 and the extra info headers are None when there is no metric source. """
        project = domain.Project(metric_sources={metric_source.Sonar: self.__sonar})
        project.metric_sources = MagicMock(return_value=[None])
        self._metric = self.metric_class(subject=self.__subject, project=project)
        self.assertEqual(-1, self._metric.value())
        self.assertEqual(None, self._metric.extra_info_headers)

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
        self.__subject.low_target = MagicMock(return_value=51)
        self.__subject.target = MagicMock(return_value=51)
        self._metric.perfect_value = 51
        self.assertEqual('perfect', self._metric.status())

    def test_norm_template_default_values(self):
        """ Test that the right values are returned to fill in the norm template. """
        self.assertTrue(self.metric_class.norm_template % self.metric_class.norm_template_default_values())

    def test_extra_info_headers(self):
        """ Test if the detail table headers are as defined. """
        self.assertEqual(
            {"violation_type": "Violation type",
             "number": "Aantal__detail-column-number",
             "debt": "Geschatte oplostijd__detail-column-number"},
            self._metric.extra_info_headers
        )

    def test_extra_info_rows(self):
        """ Unit tests for the CodeMaintainabilityMetric metric class. """

        self.__sonar.violations_type_severity = MagicMock(side_effect=[
            ('url_bugs', 1, '5min'), ('url_vulnerabilities', 3, '1h 2min'), ('url_code_smells', 5, '32min')
        ])

        result = self._metric.extra_info_rows()

        self.assertEqual([
            ({'href': 'url_bugs', 'text': 'Bugs'}, 1, '5min'),
            ({'href': 'url_vulnerabilities', 'text': 'Vulnerabilities'}, 3, '1h 2min'),
            ({'href': 'url_code_smells', 'text': 'Code Smell'}, 5, '32min')
        ], result)
        self.assertEqual(3, self.__sonar.violations_type_severity.call_count)


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
        self._sonar = MagicMock()
        self.__subject = domain.Product(short_name='PR', name='FakeSubject',
                                        metric_source_ids={self._sonar: "sonar id"})

    def test_value(self):
        """ Test that the value is equal to the number of false positives as reported by Sonar. """
        self._sonar.false_positives = MagicMock(return_value=3)
        project = domain.Project(metric_sources={metric_source.Sonar: self._sonar})
        violation_metric = metric.FalsePositives(subject=self.__subject, project=project)

        self.assertEqual(3, violation_metric.value())
        self._sonar.false_positives.assert_called_once_with('sonar id')

    def test_value_no_metric_source(self):
        """ Test that the value is equal to -1 when there is no metric source. """
        project = domain.Project(metric_sources={metric_source.Sonar: self._sonar})
        project.metric_sources = MagicMock(return_value=[None])
        violation_metric = metric.FalsePositives(subject=self.__subject, project=project)

        self.assertEqual(-1, violation_metric.value())
        self._sonar.false_positives.assert_not_called()
