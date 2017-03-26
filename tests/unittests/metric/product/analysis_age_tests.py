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
from typing import Type

from hqlib import metric, domain, metric_source


class FakeMetricSource(object):
    """ Fake metric source for unit test purposes. """
    # pylint: disable=unused-argument

    def __init__(self, age=10):
        self.age = age

    def datetime(self, *args):
        """ Return a fake analysis date time. """
        if self.age == -1:
            return datetime.datetime.min
        else:
            return datetime.datetime.now() - datetime.timedelta(days=self.age, hours=12)

    @staticmethod
    def url(*args):
        """ Return a fake metric source url. """
        return 'http://metric_source'

    @staticmethod
    def metric_source_urls(*args):
        """ Return a fake metric source urls. """
        return ['http://metric_source']


class FakeSonar(FakeMetricSource):
    """ Provide for a fake Sonar object so that the unit test don't need access to an actual Sonar instance. """
    metric_source_name = metric_source.Sonar.metric_source_name
    needs_metric_source_id = metric_source.Sonar.needs_metric_source_id

    violations_url = dashboard_url = FakeMetricSource.url


class SonarAnalysisAgeTest(unittest.TestCase):
    """ Unit tests for the sonar analysis age metric. """
    metric_source_class: Type[domain.MetricSource] = metric_source.Sonar
    metric_source_class_mock: Type[FakeMetricSource] = FakeSonar
    metric_class: Type[domain.Metric] = metric.SonarAnalysisAge
    expected_metric_source_text: str = 'De meest recente Sonar analyse'

    def setUp(self):
        self.__metric_source = self.metric_source_class_mock()
        project = domain.Project(metric_sources={self.metric_source_class: self.__metric_source})
        subject = domain.Product(short_name='PR', name='FakeSubject', metric_source_ids={self.__metric_source: 'id'})
        self.__metric = self.metric_class(subject=subject, project=project)

    def test_value(self):
        """ Test that the value of the metric equals the age of the latest analysis. """
        self.assertEqual(10, self.__metric.value())

    def test_value_today(self):
        """ Test that the value of the metric equals zero if the latest analysis was done today. """
        self.__metric_source.age = 0
        self.assertEqual(0, self.__metric.value())

    def test_missing_analysis(self):
        """ Test that the value of the metric is -1 when there is no analysis. """
        self.__metric_source.age = -1
        self.assertEqual(-1, self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({self.metric_source_class.metric_source_name: self.__metric_source.url()},
                         self.__metric.url())

    def test_report(self):
        """ Test that the report of the metric is correct. """
        self.assertEqual('{} van FakeSubject is 10 dagen oud.'.format(self.expected_metric_source_text),
                         self.__metric.report())


class FakeOWASPDependencyReport(FakeMetricSource):
    """ Provide for a fake OWASP dependency report so that the unit test don't need access to an actual report
        instance. """
    metric_source_name = metric_source.OWASPDependencyReport.metric_source_name
    needs_metric_source_id = metric_source.OWASPDependencyReport.needs_metric_source_id


class OWASPDependencyReportAgeTest(SonarAnalysisAgeTest):
    """ Unit tests for the OWASP dependency checker report age metric. """
    metric_source_class = metric_source.OWASPDependencyReport
    metric_source_class_mock = FakeOWASPDependencyReport
    metric_class = metric.OWASPDependencyReportAge
    expected_metric_source_text = 'Het meest recente OWASP dependency rapport'


class FakeOpenVASScanReport(FakeMetricSource):
    """ Provide for a fake Open VAS Scan report so that the unit test don't need access to an actual report
        instance. """
    metric_source_name = metric_source.OpenVASScanReport.metric_source_name
    needs_metric_source_id = metric_source.OpenVASScanReport.needs_metric_source_id


class OpenVASScanReportAgeTest(SonarAnalysisAgeTest):
    """ Unit tests for the Open VAS Scan report age metric. """
    metric_source_class = metric_source.OpenVASScanReport
    metric_source_class_mock = FakeOpenVASScanReport
    metric_class = metric.OpenVASScanReportAge
    expected_metric_source_text = 'Het meest recente Open VAS Scan rapport'
