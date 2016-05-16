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
    # pylint: disable=too-many-public-methods,no-member
    """ Unit tests for the Sonar metric source mixin class. """

    def test_can_be_measured(self):
        """ Test that subclasses of the Sonar metric mixin can be measured
            when the project has Sonar and the product has a Sonar id. """
        project = domain.Project(metric_sources={metric_source.Sonar: 'Sonar'})
        product = domain.Product(project, metric_source_ids={'Sonar': 'sonar id'})
        self.assertTrue(SonarMetricMixinUnderTest.can_be_measured(product, project))

    def test_cant_be_measured_without_sonar(self):
        """ Test that subclasses of the Sonar metric mixin can't be measured
            when the product has a Sonar id but the project has no Sonar. """
        project = domain.Project()
        product = domain.Product(project)
        self.assertFalse(SonarMetricMixinUnderTest.can_be_measured(product, project))

    def test_cant_be_measured_without_sonar_d(self):
        """ Test that subclasses of the Sonar metric mixin can't be measured
            when the project has Sonar but the product has no Sonar id. """
        project = domain.Project(metric_sources={metric_source.Sonar: 'Sonar'})
        product = domain.Product(project)
        self.assertFalse(SonarMetricMixinUnderTest.can_be_measured(product, project))


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
    def has_test_design(*args):  # pylint: disable=unused-argument
        """ Return whether the Birt instance has a test design report. """
        return True


class BirtTestDesignMixinTest(unittest.TestCase):
    """ Unit tests for the Birt test design report metric source mixin class. """
    # pylint: disable=no-member

    def test_one_birt(self):
        """ Test that the metric can be measured with one Birt instance. """
        birt = FakeBirt()
        project = domain.Project(metric_sources={metric_source.Birt: birt})
        product = domain.Product(project, metric_source_ids={birt: 'birt id'})
        self.assertTrue(BirtTestDesignMetricUnderTest.can_be_measured(product, project))

    def test_multiple_birts(self):
        """ Test that the metric can be measured with multiple Birt instances. """
        project = domain.Project(metric_sources={metric_source.Birt: ['Birt1', 'Birt2']})
        product = domain.Product(project, metric_source_ids={'Birt1': 'birt id'})
        self.assertTrue(BirtTestDesignMetricUnderTest.can_be_measured(product, project))
