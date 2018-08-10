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
from unittest.mock import MagicMock, call

from typing import Type

from hqlib import metric, domain, metric_source
from hqlib.metric.product.alerts_metrics import AlertsMetric
from hqlib.metric_source.abstract.owasp_dependency_report import Dependency


class HighPriorityOWASPDependencyWarningsTest(unittest.TestCase):
    """ Unit tests for the high priority OWASP dependency warnings metric. """

    class_under_test: Type[AlertsMetric] = metric.HighPriorityOWASPDependencyWarnings  # May be overridden

    def setUp(self):
        self.__metric_source = MagicMock()
        self.__metric_source.nr_warnings = MagicMock(return_value=4)
        self.__metric_source.metric_source_name = metric_source.JenkinsOWASPDependencyReport.metric_source_name
        self.__subject = MagicMock()
        self.__subject.name = MagicMock(return_value='X')
        self.__subject.metric_source_id = MagicMock(return_value=['X', 'Y'])
        self.__project = domain.Project(metric_sources={metric_source.OWASPDependencyReport: self.__metric_source})
        self.__project.metric_sources = MagicMock(return_value=[self.__metric_source])
        self.__metric = self.class_under_test(subject=self.__subject, project=self.__project)

    def expected_warnings(self, job):
        """ Return the number of expected warnings. """
        return self.__metric_source.nr_warnings(job, self.class_under_test.risk_level_key)

    def test_value(self):
        """ Test that value of the metric equals the number of warnings as reported by Jenkins. """
        self.assertEqual(self.expected_warnings('jenkins_job'), self.__metric.value())

    def test_extra_info_rows(self):
        """ Test that extra info urls of the metric are as expected. """
        expected_dependencies = [Dependency("dep1", 3, ["url", "text"])]
        self.__metric_source.get_dependencies_info = MagicMock(return_value=expected_dependencies)

        result = self.__metric.extra_info_rows()

        self.assertEqual(expected_dependencies + expected_dependencies, result)
        self.assertEqual(call('X', self.__metric.risk_level_key),
                         self.__metric_source.get_dependencies_info.call_args_list[0])
        self.assertEqual(call('Y', self.__metric.risk_level_key),
                         self.__metric_source.get_dependencies_info.call_args_list[1])

    def test_convert_item_to_extra_info(self):
        """ Test the conversion of dependency record to extra info. """
        depend = Dependency("dep1", 3, [("text", "url"), ("text2", "url2")])
        self.assertEqual((depend.file_name, depend.nr_vulnerabilities,
                          ({'href': 'url', 'text': 'text'}, {'href': 'url2', 'text': 'text2'})),
                         self.__metric.convert_item_to_extra_info(depend))

    def test_value_multiple_jobs(self):
        """ Test that the value of the metric equals the number of warnings if there are multiple
            test reports. """
        self.__subject.metric_source_id = MagicMock(return_value=['a', 'b'])
        self.assertEqual(self.expected_warnings(['a', 'b']), self.__metric.value())

    def test_value_without_metric_source(self):
        """ Test that the value is -1 when no OWASP dependency report is provided. """
        owasp = self.class_under_test(subject=self.__subject, project=domain.Project())
        self.assertEqual(-1, owasp.value())

    def test_report(self):
        """ Test that the report for the metric is correct. """
        expected_report = 'Dependencies van X hebben {0} {1} prioriteit waarschuwingen.'.format(
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
        owasp = self.class_under_test(None, self.__project)
        self.assertTrue(owasp._missing())  # pylint: disable=protected-access

    def test_is_not_missing(self):
        """ Test that the metric is not missing when Jenkins is available. """
        self.assertFalse(self.__metric._missing())  # pylint: disable=protected-access


class NormalPriorityOWASPDependencyWarningsTest(HighPriorityOWASPDependencyWarningsTest):
    """ Unit tests for the normal priority OWASP dependency warnings metric. """

    class_under_test = metric.NormalPriorityOWASPDependencyWarnings
