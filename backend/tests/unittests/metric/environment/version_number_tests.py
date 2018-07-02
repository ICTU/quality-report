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
from distutils.version import LooseVersion

from hqlib import metric, domain, metric_source


class FakeSonar(object):
    """ Provide for a fake Sonar object so that the unit test don't need access to an actual Sonar instance. """

    metric_source_name = metric_source.Sonar.metric_source_name

    @staticmethod
    def version_number():
        """ Return a fake version number. """
        return '999.4.1.4'

    @staticmethod
    def plugin_version(plugin):
        """ Return a fake plugin version number. """
        return '11.4' if plugin == 'java' else '0.0'

    @staticmethod
    def default_quality_profile(language):
        """ Return a fake default profile. """
        return "Java profile v1.6-20151008" if language == 'java' else ''

    @staticmethod
    def url():
        """ Return the Sonar url. """
        return 'http://sonar/'


class SonarVersionTest(unittest.TestCase):
    """ Unit tests for the SonarVersion metric. """
    def setUp(self):
        sonar = FakeSonar()
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        environment = domain.Environment(metric_source_ids={sonar: 'dummy'})
        self.__metric = metric.SonarVersion(project=project, subject=environment)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(FakeSonar().version_number(), self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual("Sonar is versie 999.4.1.4.", self.__metric.report())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({FakeSonar.metric_source_name: FakeSonar().url()}, self.__metric.url())

    def test_url_empty(self):
        """ Test that the url is empty for empty metric source. """
        project = domain.Project(metric_sources={metric_source.Sonar: []})
        environment = domain.Environment(metric_source_ids={FakeSonar(): 'dummy'})
        self.__metric = metric.SonarVersion(project=project, subject=environment)
        self.assertEqual({}, self.__metric.url())

    def test_status(self):
        """ Test that the metric is green. """
        self.assertEqual('green', self.__metric.status())

    def test_numerical_value(self):
        """ Test that the numerical value is a weighted sum of the first three version number parts. """
        self.assertEqual(9990401, self.__metric.numerical_value())

    def test_missing(self):
        """ Test that the value is -1 without a metric source. """
        self.assertEqual(-1, metric.SonarVersion(project=domain.Project(), subject=domain.Environment()).value())


class SonarQualityProfileVersionTest(unittest.TestCase):
    """ Unit tests for the Sonar quality profile version metric. """
    def setUp(self):
        sonar = FakeSonar()
        self.__project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        self.__environment = domain.Environment(metric_source_ids={sonar: 'dummy'})
        self.__metric = metric.SonarQualityProfileVersionJava(project=self.__project, subject=self.__environment)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(LooseVersion('1.6'), self.__metric.value())

    def test_value_when_missing(self):
        """ Test that the value is '0.0' when the plugin is missing. """
        version = metric.SonarQualityProfileVersionCSharp(project=self.__project, subject=self.__environment)
        self.assertEqual(LooseVersion('0.0'), version.value())

    def test_value_with_multiple_sources(self):
        """ Test that the value is '0.0' when multiple metric source have been configured, but not metric source id. """
        sonar1, sonar2 = FakeSonar(), FakeSonar()
        version = metric.SonarQualityProfileVersionJava(
            project=domain.Project(metric_sources={metric_source.Sonar: [sonar1, sonar2]}),
            subject=domain.Environment())
        self.assertEqual(LooseVersion('0.0'), version.value())

    def test_numerical_value(self):
        """ Test that the numerical value is a weighted sum of the first three version number parts. """
        self.assertEqual(10600, self.__metric.numerical_value())

    def test_numerical_value_when_missing(self):
        """ Test that the numerical value is -1 when the plugin is missing. """
        version = metric.SonarQualityProfileVersionCSharp(project=self.__project, subject=self.__environment)
        self.assertEqual(-1, version.numerical_value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual("Sonar Java quality profile is versie 1.6.", self.__metric.report())

    def test_status(self):
        """ Test that the metric is red. """
        self.assertEqual('red', self.__metric.status())

    def test_norm_template(self):
        """ Test that the plugin name is filled in correctly in the norm template. """
        values = metric.SonarQualityProfileVersionJava.norm_template_default_values()
        self.assertEqual('Sonar Java quality profile heeft minimaal versie 1.8, lager dan versie 1.7 is rood.',
                         metric.SonarQualityProfileVersionJava.norm_template.format(**values))


class SonarPluginVersionTest(unittest.TestCase):
    """ Unit tests for the SonarPluginVersion class and its subclasses. """
    def setUp(self):
        sonar = FakeSonar()
        self.__project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        self.__environment = domain.Environment(metric_source_ids={sonar: 'dummy'})
        self.__metric = metric.SonarPluginVersionJava(project=self.__project, subject=self.__environment)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(FakeSonar().plugin_version(self.__metric.plugin_key), self.__metric.value())

    def test_value_when_missing(self):
        """ Test that the value is '0.0' when the plugin is missing. """
        version = metric.SonarPluginVersionCSharp(project=self.__project, subject=self.__environment)
        self.assertEqual(LooseVersion('0.0'), version.value())

    def test_value_with_multiple_sources(self):
        """ Test that the value is '0.0' when multiple metric source have been configured, but not metric source id. """
        sonar1, sonar2 = FakeSonar(), FakeSonar()
        version = metric.SonarPluginVersionJava(
            project=domain.Project(metric_sources={metric_source.Sonar: [sonar1, sonar2]}),
            subject=domain.Environment())
        self.assertEqual(LooseVersion('0.0'), version.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual("Sonar plugin Java is versie 11.4.", self.__metric.report())

    def test_status(self):
        """ Test that the metric is green. """
        self.assertEqual('green', self.__metric.status())

    def test_numerical_value(self):
        """ Test that the numerical value is a weighted sum of the first three version number parts. """
        self.assertEqual(110400, self.__metric.numerical_value())

    def test_norm_template(self):
        """ Test that the plugin name is filled in correctly in the norm template. """
        values = metric.SonarPluginVersionJava.norm_template_default_values()
        self.assertEqual('Sonar plugin Java heeft minimaal versie 3.14, lager dan versie 3.13.1 is rood.',
                         metric.SonarPluginVersionJava.norm_template.format(**values))
