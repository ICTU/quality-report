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

from hqlib import metric, domain, metric_source


class FakeSonar(object):
    """ Provide for a fake Sonar object so that the unit test don't need access to an actual Sonar instance. """
    # pylint: disable=unused-argument

    metric_source_name = metric_source.Sonar.metric_source_name

    def __init__(self, age=10):
        self.age = age

    def analysis_datetime(self, *args):
        """ Return a fake dashboard url. """
        if self.age == -1:
            return datetime.datetime.min
        else:
            return datetime.datetime.now() - datetime.timedelta(days=self.age, hours=12)

    @staticmethod
    def dashboard_url(*args):
        """ Return a fake dashboard url. """
        return 'http://sonar'

    url = violations_url = dashboard_url


class SonarAnalysisAgeTest(unittest.TestCase):
    """ Unit tests for the sonar analysis age metric. """

    def setUp(self):
        self.__sonar = FakeSonar()
        project = domain.Project(metric_sources={metric_source.Sonar: self.__sonar})
        subject = domain.Product(project, 'PR', name='FakeSubject')
        self.__metric = metric.SonarAnalysisAge(subject=subject, project=project)

    def test_value(self):
        """ Test that the value of the metric equals the date of the latest analysis. """
        self.assertEqual(10, self.__metric.value())

    def test_value_today(self):
        """ Test that the value of the metric equals zero if the latest analysis was done today. """
        self.__sonar.age = 0
        self.assertEqual(0, self.__metric.value())

    def test_missing_analysis(self):
        """ Test that the value of the metric is -1 when there is no analysis. """
        self.__sonar.age = -1
        self.assertEqual(-1, self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({FakeSonar.metric_source_name: FakeSonar.dashboard_url()}, self.__metric.url())

    def test_report(self):
        """ Test that the report of the metric is correct. """
        self.assertEqual('De meest recente Sonar analyse van FakeSubject is 10 dagen oud.', self.__metric.report())
