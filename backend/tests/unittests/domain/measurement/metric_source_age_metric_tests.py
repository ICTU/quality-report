"""
Copyright 2012-2017 Ministerie van Sociale Zaken en Werkgelegenheid

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

from hqlib import domain


class FakeMetricSource(domain.MetricSource):
    """ Fake metric source for the unit tests below. """
    needs_metric_source_id = True

    @staticmethod
    def datetime(*args):  # pylint: disable=unused-argument
        """ Return the date and time the metric source was last updated. """
        return datetime.datetime.now() - datetime.timedelta(seconds=5)


class MetricSourceAgeMetricUnderTest(domain.MetricSourceAgeMetric):
    """ Implement abstract methods. """
    metric_source_class = FakeMetricSource


class MetricSourceAgeMetricTest(unittest.TestCase):
    """ Test case for the metric source age metric. """

    def setUp(self):
        self.__metric_source = FakeMetricSource()
        self.__subject = domain.Product(name='Product', metric_source_ids={self.__metric_source: 'http://url'})
        self.__project = domain.Project(metric_sources={FakeMetricSource: self.__metric_source})
        self.__metric = MetricSourceAgeMetricUnderTest(self.__subject, project=self.__project)

    def test_value(self):
        """ Test the value of the metric. """
        self.assertEqual(0, self.__metric.value())

    def test_status(self):
        """ Test that the default status is perfect. """
        self.assertEqual('perfect', self.__metric.status())

    def test_missing_source(self):
        """ Test that the status is missing_source if the project has no metric source. """
        metric = MetricSourceAgeMetricUnderTest(self.__subject, project=domain.Project())
        self.assertEqual('missing_source', metric.status())

    def test_value_with_missing_source(self):
        """ Test that the status is missing_source if the project has no metric source. """
        metric = MetricSourceAgeMetricUnderTest(self.__subject,
                                                project=domain.Project(metric_sources={FakeMetricSource: None}))
        self.assertEqual(-1, metric.value())

    def test_missing_metric_source_id(self):
        """ Test that the status is missing_source if the subject has no metric source id. """
        metric = MetricSourceAgeMetricUnderTest(domain.Product(name='Product'), project=self.__project)
        self.assertEqual('missing_source', metric.status())

    def test_norm_template_default_values(self):
        """ Test that the right values are returned to fill in the norm template. """
        self.assertTrue(MetricSourceAgeMetricUnderTest.norm_template %
                        MetricSourceAgeMetricUnderTest.norm_template_default_values())

    def test_url(self):
        """ Test that the url of the metric equals the metric source id. """
        self.assertEqual({FakeMetricSource.metric_source_name: 'http://url'}, self.__metric.url())

    def test_report(self):
        """ Test the metric report. """
        self.assertEqual('Subclass responsibility', self.__metric.report())

    def test_norm(self):
        """ Test that the norm is correct. """
        self.assertEqual('Subclass responsibility', self.__metric.norm())
