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

import unittest

from hqlib import domain, metric_source
from hqlib.metric.metric_source_mixin import SonarMetric, BirtTestDesignMetric


class SonarMetricTest(unittest.TestCase):
    """ Unit tests for the Sonar metric source class. """

    def test_url(self):
        """ Test the url. """
        sonar = metric_source.Sonar('http://sonar/')
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        product = domain.Product(metric_source_ids={sonar: 'sonar id'})
        self.assertEqual({sonar.metric_source_name: sonar.url()}, SonarMetric(product, project).url())

    def test_url_without_sonar(self):
        """ Test that the metric has no url when the project has no Sonar configured. """
        project = domain.Project()
        product = domain.Product()
        self.assertEqual(dict(), SonarMetric(product, project).url())

    def test_url_without_sonar_id(self):
        """ Test that the metric has a url when the product has no Sonar id configured. """
        sonar = metric_source.Sonar('http://sonar/')
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        product = domain.Product()
        self.assertEqual({sonar.metric_source_name: sonar.url()}, SonarMetric(product, project).url())


class FakeBirt(object):
    """ Fake a Birt instance for test purposes. """
    # pylint: disable=too-few-public-methods

    metric_source_name = metric_source.Birt.metric_source_name
    needs_metric_source_id = metric_source.Birt.needs_metric_source_id

    @staticmethod
    def whats_missing_url():
        """ Return the url for the What's Missing report. """
        return 'http://birt/whatsmissing/'


class BirtTestDesignMetricTest(unittest.TestCase):
    """ Unit tests for the Birt test design report metric source class. """

    def test_url(self):
        """ Test the url. """
        birt = FakeBirt()
        project = domain.Project(metric_sources={metric_source.Birt: birt})
        product = domain.Product(metric_source_ids={birt: 'birt id'})
        self.assertEqual({birt.metric_source_name: birt.whats_missing_url()},
                         BirtTestDesignMetric(product, project).url())

    def test_url_with_multiple_birts(self):
        """ Test the url with multiple Birt instances. """
        birt1, birt2 = FakeBirt(), FakeBirt()
        project = domain.Project(metric_sources={metric_source.Birt: [birt1, birt2]})
        product = domain.Product(metric_source_ids={birt1: 'birt id'})
        self.assertEqual({birt1.metric_source_name: birt1.whats_missing_url()},
                         BirtTestDesignMetric(product, project).url())

    def test_url_without_birt(self):
        """ Test that the metric has no url when Birt hasn't been configured. """
        project = domain.Project()
        product = domain.Product()
        self.assertEqual(dict(), BirtTestDesignMetric(product, project).url())

    def test_url_without_birt_id(self):
        """ Test that the metric has no url when the product has no Birt id. """
        birt = FakeBirt()
        project = domain.Project(metric_sources={metric_source.Birt: birt})
        product = domain.Product()
        self.assertEqual({birt.metric_source_name: birt.whats_missing_url()},
                         BirtTestDesignMetric(product, project).url())
