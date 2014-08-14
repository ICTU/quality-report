'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import unittest
from qualitylib import metric, domain, metric_source


class FakeSonar(object):
    ''' Provide for a fake Sonar object so that the unit test don't need 
        access to an actual Sonar instance. '''
    # pylint: disable=unused-argument

    @staticmethod
    def dashboard_url(*args):  
        ''' Return a fake dashboard url. '''
        return 'http://sonar'

    url = violations_url = dashboard_url

    @staticmethod
    def ncloc(*args):
        ''' Return the number of non-comment LOC. '''
        return 123

    @staticmethod
    def commented_loc(*args):
        ''' Return the number of lOC that are commented out. '''
        return 10

    @staticmethod
    def complex_methods(*args):
        ''' Return the number of methods that are too complex. '''
        return 5

    long_methods = many_parameters_methods = complex_methods

    @staticmethod
    def methods(*args):
        ''' Return the number of methods. '''
        return 100


class FakeSubject(object):
    ''' Provide for a fake subject. '''

    @staticmethod
    def name():
        ''' Return the name of the subject. '''
        return 'FakeSubject'

    @staticmethod
    def sonar_id():
        ''' Return the Sonar id of the subject. '''
        return ''

    @staticmethod  # pylint: disable-msg=unused-argument
    def responsible_teams(*args):
        ''' Return the responsible teams for this product. '''
        return [domain.Team(name='Team')]


class SonarViolationsUrlTestMixin(object):
    # pylint: disable=too-few-public-methods
    ''' Mixin for metrics whose url refers to the Sonar violations page. '''
    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(dict(Sonar=FakeSonar().violations_url()),
                         self._metric.url())


class CommentedLOCTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the commented LOC metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__subject = FakeSubject()
        project = domain.Project(
            metric_sources={metric_source.Sonar: FakeSonar()})
        self._metric = metric.CommentedLOC(subject=self.__subject,
                                           project=project)

    def test_value(self):
        ''' Test that the value of the metric equals the percentage of 
            LOC that is commented out. '''
        self.assertEqual(8.0, self._metric.value())

    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(dict(Sonar=FakeSonar().dashboard_url()), 
                         self._metric.url())


class CyclomaticComplexityTest(SonarViolationsUrlTestMixin, unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the Cyclomatic complexity metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        project = domain.Project(
            metric_sources={metric_source.Sonar: FakeSonar()})
        self._metric = metric.CyclomaticComplexity(subject=FakeSubject(),
                                                   project=project)

    def test_value(self):
        ''' Test that the value of the metric equals the percentage of 
            methods that are too complex. '''
        self.assertEqual(5.0, self._metric.value())

    def test_report(self):
        ''' Test that the report of the metric is correct. '''
        self.assertEqual('5% van de methoden (5 van 100) van FakeSubject ' \
                         'heeft een cyclomatische complexiteit van 10 of ' \
                         'hoger.', self._metric.report())

    def test_norm_template_default_values(self):
        ''' Test that the right values are returned to fill in the norm 
            template. '''
        self.failUnless(metric.CyclomaticComplexity.norm_template % \
            metric.CyclomaticComplexity.norm_template_default_values())


class LongMethodsTest(SonarViolationsUrlTestMixin, unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the long methods metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        project = domain.Project(
            metric_sources={metric_source.Sonar: FakeSonar()})
        self._metric = metric.LongMethods(subject=FakeSubject(),
                                          project=project)

    def test_value(self):
        ''' Test that the value of the metric equals the percentage of 
            long methods. '''
        self.assertEqual(5., self._metric.value())

    def test_report(self):
        ''' Test that the report of the metric is correct. '''
        self.assertEqual('5% van de methoden (5 van 100) van FakeSubject ' \
                         'heeft een lengte van meer dan 20 NCSS ' \
                         '(Non-Comment Source Statements).', 
                         self._metric.report())

    def test_norm_template_default_values(self):
        ''' Test that the right values are returned to fill in the norm 
            template. '''
        self.failUnless(metric.LongMethods.norm_template % \
            metric.LongMethods.norm_template_default_values())


class ManyParametersTest(SonarViolationsUrlTestMixin, unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the many parameters metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        project = domain.Project(metric_sources={metric_source.Sonar: FakeSonar()})
        self._metric = metric.ManyParameters(subject=FakeSubject(),
                                             project=project)

    def test_value(self):
        ''' Test that the value of the metric equals the percentage of 
            methods with too many parameters. '''
        self.assertEqual(5., self._metric.value())

    def test_report(self):
        ''' Test that the report of the metric is correct. '''
        self.assertEqual('5% van de methoden (5 van 100) van FakeSubject ' \
                         'heeft meer dan 5 parameters.', self._metric.report())

    def test_norm_template_default_values(self):
        ''' Test that the right values are returned to fill in the norm 
            template. '''
        self.failUnless(metric.ManyParameters.norm_template % \
            metric.ManyParameters.norm_template_default_values())
