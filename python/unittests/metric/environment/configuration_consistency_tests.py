"""
Copyright 2012-2016 Ministerie van Sociale Zaken en Werkgelegenheid

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

from qualitylib import metric, domain, metric_source


class FakeAnsibleConfigReport(object):
    """ Fake Ansible configuration report instance for testing purposes. """
    # pylint: disable=unused-argument

    report_date = datetime.datetime.now()
    report_java_versions = 2

    def java_versions(self, *args):
        """ Return the number of different java versions. """
        return self.report_java_versions

    def date(self, *args):
        """ Return the date of the report. """
        return self.report_date


class JavaVersionConsistencyTests(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the configuration consistency metric. """

    def setUp(self):  # pylint: disable=invalid-name
        """ Create the text fixture. """
        self.__report = FakeAnsibleConfigReport()
        self.__project = domain.Project(metric_sources={metric_source.AnsibleConfigReport: self.__report},
                                        metric_source_ids={self.__report: 'http://ansible_report'})
        self.__metric = metric.JavaVersionConsistency(subject=self.__project, project=self.__project)

    def test_can_be_measured(self):
        """ Test that the metric can be measured if there is a config report. """
        self.assertTrue(metric.JavaVersionConsistency.can_be_measured(self.__project, self.__project))

    def test_cant_be_measured_without_config_report(self):
        """ Test that the metric cannot be measured without config report. """
        project = domain.Project()
        self.assertFalse(metric.JavaVersionConsistency.can_be_measured(project, project))

    def test_norm_template_default_values(self):
        """ Test that the right values are returned to fill in the norm template. """
        self.assertTrue(metric.JavaVersionConsistency.norm_template %
                        metric.JavaVersionConsistency.norm_template_default_values())

    def test_value(self):
        """ Test that the value equals the number of differences. """
        self.assertEqual(2, self.__metric.value())

    def test_url(self):
        """ Test that the url of the metric equals the url of Jenkins. """
        self.assertEqual({'Ansible configuration report': 'http://ansible_report'}, self.__metric.url())

    def test_report(self):
        """ Test the metric report. """
        self.assertEqual('Er zijn 2 verschillende versies van Java in gebruik.', self.__metric.report())

    def test_norma(self):
        """ Test that the norm is correct. """
        self.assertEqual('Er is precies een versie van Java in gebruik. Meer dan 2 versies is rood. '
                         'De rapportage is maximaal 3 dagen oud. Meer dan 7 dagen oud is rood.',
                         self.__metric.norm())

    def test_status_with_recent_report(self):
        """ Test that the metric is perfect when there are no different versions. """
        self.__report.report_java_versions = 1
        self.assertEqual('perfect', self.__metric.status())

    def test_status_with_old_report(self):
        """ Test that the metric is red when the report is old. """
        self.__report.report_java_versions = 1
        self.__report.report_date = datetime.datetime(2015, 1, 1)
        self.assertEqual('red', self.__metric.status())
