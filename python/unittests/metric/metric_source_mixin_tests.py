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

import unittest

from qualitylib import metric, domain, metric_source


class SonarMetricMixinUnderTest(metric.SonarMetricMixin, metric.Metric):
    """ Create a testable class by mixing the mixin class with a metric class. """
    # pylint: disable=too-few-public-methods
    pass


class SonarMetricMixinTest(unittest.TestCase):
    """ Unit tests for the Sonar metric source mixin class. """

    def test_url(self):
        """ Test the url. """
        sonar = metric_source.Sonar('http://sonar/')
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        product = domain.Product(project, metric_source_ids={sonar: 'sonar id'})
        self.assertEqual(dict(Sonar='http://sonar/'), SonarMetricMixinUnderTest(product, project).url())

    def test_url_without_sonar(self):
        """ Test that the metric has no url when the project has no Sonar configured. """
        project = domain.Project()
        product = domain.Product(project)
        self.assertEqual(dict(), SonarMetricMixinUnderTest(product, project).url())

    def test_url_without_sonar_id(self):
        """ Test that the metric has a url when the product has no Sonat id configured. """
        sonar = metric_source.Sonar('http://sonar/')
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        product = domain.Product(project)
        self.assertEqual(dict(Sonar='http://sonar/'), SonarMetricMixinUnderTest(product, project).url())


class BirtMetricUnderTest(metric.BirtMetricMixin, domain.Metric):
    """ Create a testable class by mixing the mixin class with a metric class. """
    # pylint: disable=too-few-public-methods
    pass


class BirtMetricMixinTest(unittest.TestCase):
    """ Unit tests for the Birt metric source mixin class. """
    # pylint: disable=protected-access

    def test_one_birt(self):
        """ Test that the correct Birt id is returned when there is one Birt instance. """
        project = domain.Project(metric_sources={metric_source.Birt: 'Birt1'})
        product = domain.Product(project, metric_source_ids={'Birt1': 'birt id'})
        self.assertEqual('birt id', BirtMetricUnderTest(project=project, subject=product)._birt_id())

    def test_multiple_birts(self):
        """ Test that the correct Birt id is returned when there are multiple Birt instances. """
        project = domain.Project(metric_sources={metric_source.Birt: ['Birt1', 'Birt2']})
        product = domain.Product(project, metric_source_ids={'Birt2': 'birt id'})
        self.assertEqual('birt id', BirtMetricUnderTest(project=project, subject=product)._birt_id())

    def test_no_matching_birt(self):
        """ Test that no Birt id is returned when there is no Birt instance for the product. """
        project = domain.Project(metric_sources={metric_source.Birt: ['Birt1']})
        product = domain.Product(project, metric_source_ids={'Birt2': 'birt id'})
        self.failIf(BirtMetricUnderTest(project=project, subject=product)._birt_id())


class BirtTestDesignMetricUnderTest(metric.BirtTestDesignMetricMixin, domain.Metric):
    """ Create a testable class by mixing the mixin class with a metric class. """
    # pylint: disable=too-few-public-methods
    pass


class FakeBirt(object):
    """ Fake a Birt instance for test purposes. """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def whats_missing_url(*args):  # pylint: disable=unused-argument
        """ Return the url for the What's Missing report. """
        return 'http://birt/whatsmissing/'


class BirtTestDesignMixinTest(unittest.TestCase):
    """ Unit tests for the Birt test design report metric source mixin class. """

    def test_url(self):
        """ Test the url. """
        birt = FakeBirt()
        project = domain.Project(metric_sources={metric_source.Birt: birt})
        product = domain.Product(project, metric_source_ids={birt: 'birt id'})
        self.assertEqual(dict(Birt='http://birt/whatsmissing/'), BirtTestDesignMetricUnderTest(product, project).url())

    def test_url_with_multiple_birts(self):
        """ Test the url with multiple Birt instances. """
        birt1, birt2 = FakeBirt(), FakeBirt()
        project = domain.Project(metric_sources={metric_source.Birt: [birt1, birt2]})
        product = domain.Product(project, metric_source_ids={birt1: 'birt id'})
        self.assertEqual(dict(Birt='http://birt/whatsmissing/'), BirtTestDesignMetricUnderTest(product, project).url())

    def test_url_without_birt(self):
        """ Test that the metric has no url when Birt hasn't been configured. """
        project = domain.Project()
        product = domain.Product(project)
        self.assertEqual(dict(), BirtTestDesignMetricUnderTest(product, project).url())

    def test_url_without_birt_id(self):
        """ Test that the metric has no url when the product has no Birt id. """
        birt = FakeBirt()
        project = domain.Project(metric_sources={metric_source.Birt: birt})
        product = domain.Product(project)
        self.assertEqual(dict(Birt='http://birt/whatsmissing/'), BirtTestDesignMetricUnderTest(product, project).url())
