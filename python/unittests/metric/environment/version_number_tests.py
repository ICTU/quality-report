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

from __future__ import absolute_import

from qualitylib import metric, domain, metric_source
import unittest


class FakeSonar(object):
    """ Provide for a fake Sonar object so that the unit test don't need
        access to an actual Sonar instance. """

    @staticmethod
    def version_number():
        """ Return a fake version number. """
        return '5.4.1.4'

    @staticmethod
    def plugin_version(*args):  # pylint: disable=unused-argument
        """ Return a fake plugin version number. """
        return '11.4'

    @staticmethod
    def url():
        """ Return the Sonar url. """
        return 'http://sonar/'


class SonarVersionTest(unittest.TestCase):
    """ Unit tests for the SonarVersion metric. """
    def setUp(self):  # pylint: disable=invalid-name
        project = domain.Project(metric_sources={metric_source.Sonar: FakeSonar()})
        self.__metric = metric.SonarVersion(project=project)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(FakeSonar().version_number(), self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual("Sonar is versie 5.4.1.4.", self.__metric.report())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual(dict(Sonar=FakeSonar().url()), self.__metric.url())

    def test_status(self):
        """ Test that the metric is green. """
        self.assertEqual('green', self.__metric.status())

    def test_numerical_value(self):
        """ Test that the numerical value is a weighted sum of the first three version number parts. """
        self.assertEqual(50401, self.__metric.numerical_value())


class SonarPluginVersionJavaTest(unittest.TestCase):
    """ Unit tests for the SonarPluginVersion class and its subclasses. """
    def setUp(self):  # pylint: disable=invalid-name
        project = domain.Project(metric_sources={metric_source.Sonar: FakeSonar()})
        self.__metric = metric.SonarPluginVersionJava(project=project)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(FakeSonar().plugin_version(self.__metric.plugin_key), self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual("Sonar plugin Java is versie 11.4.", self.__metric.report())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual(dict(Sonar=FakeSonar().url()), self.__metric.url())

    def test_status(self):
        """ Test that the metric is green. """
        self.assertEqual('green', self.__metric.status())

    def test_numerical_value(self):
        """ Test that the numerical value is a weighted sum of the first three version number parts. """
        self.assertEqual(110400, self.__metric.numerical_value())
