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

    @staticmethod
    def dashboard_url(*args):
        """ Return a fake dashboard url. """
        return 'http://sonar'

    url = violations_url = dashboard_url

    @staticmethod
    def ncloc(*args):
        """ Return the number of non-comment LOC. """
        return 123

    @staticmethod
    def commented_loc(*args):
        """ Return the number of lOC that are commented out. """
        return 10

    @staticmethod
    def complex_methods(*args):
        """ Return the number of methods that are too complex. """
        return 5

    long_methods = many_parameters_methods = complex_methods

    @staticmethod
    def methods(*args):
        """ Return the number of methods. """
        return 100

    @staticmethod
    def no_sonar(*args):
        """ Return the number of //NOSONAR usages. """
        return 4


class SonarViolationsUrlTestMixin(object):
    # pylint: disable=too-few-public-methods
    """ Mixin for metrics whose url refers to the Sonar violations page. """
    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({FakeSonar.metric_source_name: FakeSonar().violations_url()}, self._metric.url())


class CommentedLOCTest(unittest.TestCase):
    """ Unit tests for the commented LOC metric. """

    def setUp(self):
        sonar = FakeSonar()
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        self.__subject = domain.Product(short_name='PR', name='FakeSubject', metric_source_ids={sonar: "sonar id"})
        self._metric = metric.CommentedLOC(subject=self.__subject, project=project)

    def test_value(self):
        """ Test that the value of the metric equals the percentage of LOC that is commented out. """
        self.assertEqual(8.0, self._metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({FakeSonar.metric_source_name: FakeSonar().dashboard_url()}, self._metric.url())


class CyclomaticComplexityTest(SonarViolationsUrlTestMixin, unittest.TestCase):
    """ Unit tests for the Cyclomatic complexity metric. """

    def setUp(self):
        sonar = FakeSonar()
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        subject = domain.Product(short_name='PR', name='FakeSubject', metric_source_ids={sonar: "sonar id"})
        self._metric = metric.CyclomaticComplexity(subject=subject, project=project)

    def test_value(self):
        """ Test that the value of the metric equals the percentage of methods that are too complex. """
        self.assertEqual(5.0, self._metric.value())

    def test_report(self):
        """ Test that the report of the metric is correct. """
        self.assertEqual('5% van de methoden (5 van 100) van FakeSubject heeft een cyclomatische complexiteit van '
                         '10 of hoger.', self._metric.report())

    def test_norm_template_default_values(self):
        """ Test that the right values are returned to fill in the norm template. """
        self.assertTrue(metric.CyclomaticComplexity.norm_template.format(
            **metric.CyclomaticComplexity.norm_template_default_values()))


class LongMethodsTest(SonarViolationsUrlTestMixin, unittest.TestCase):
    """ Unit tests for the long methods metric. """

    def setUp(self):
        sonar = FakeSonar()
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        subject = domain.Product(short_name='PR', name='FakeSubject', metric_source_ids={sonar: "sonar id"})
        self._metric = metric.LongMethods(subject=subject, project=project)

    def test_value(self):
        """ Test that the value of the metric equals the percentage of long methods. """
        self.assertEqual(5., self._metric.value())

    def test_report(self):
        """ Test that the report of the metric is correct. """
        self.assertEqual('5% van de methoden (5 van 100) van FakeSubject heeft een lengte van meer dan 20 NCSS '
                         '(Non-Comment Source Statements).', self._metric.report())

    def test_norm_template_default_values(self):
        """ Test that the right values are returned to fill in the norm template. """
        self.assertTrue(metric.LongMethods.norm_template.format(**metric.LongMethods.norm_template_default_values()))


class ManyParametersTest(SonarViolationsUrlTestMixin, unittest.TestCase):
    """ Unit tests for the many parameters metric. """

    def setUp(self):
        sonar = FakeSonar()
        subject = domain.Product(short_name='PR', name='FakeSubject', metric_source_ids={sonar: "sonar id"})
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        self._metric = metric.ManyParameters(subject=subject, project=project)

    def test_value(self):
        """ Test that the value of the metric equals the percentage of methods with too many parameters. """
        self.assertEqual(5., self._metric.value())

    def test_report(self):
        """ Test that the report of the metric is correct. """
        self.assertEqual('5% van de methoden (5 van 100) van FakeSubject heeft meer dan 5 parameters.',
                         self._metric.report())

    def test_norm_template_default_values(self):
        """ Test that the right values are returned to fill in the norm template. """
        self.assertTrue(metric.ManyParameters.norm_template.format(
            **metric.ManyParameters.norm_template_default_values()))


class NoSonarTest(SonarViolationsUrlTestMixin, unittest.TestCase):
    """ Unit tests for the no Sonar metric. """

    def setUp(self):
        sonar = FakeSonar()
        subject = domain.Product(short_name='PR', name='FakeSubject', metric_source_ids={sonar: "sonar id"})
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        self._metric = metric.NoSonar(subject=subject, project=project)

    def test_value(self):
        """ Test that the value of the metric equals the number of times //NOSONAR was used. """
        self.assertEqual(4, self._metric.value())

    def test_report(self):
        """ Test that the report of the metric is correct. """
        self.assertEqual('FakeSubject bevat 4 violation-onderdrukkingen.', self._metric.report())

    def test_norm_template_default_values(self):
        """ Test that the right values are returned to fill in the norm template. """
        self.assertTrue(metric.NoSonar.norm_template.format(**metric.NoSonar.norm_template_default_values()))
