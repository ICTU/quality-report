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
from unittest.mock import patch

from hqlib import domain, metric_source
from hqlib.metric.metric_source_mixin import SonarMetric


class SonarMetricTest(unittest.TestCase):
    """ Unit tests for the Sonar metric source class. """

    def test_url(self):
        """ Test the url. """
        with patch.object(metric_source.Sonar, 'version_number') as mock_version_number:
            mock_version_number.return_value = '6.3'
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
        with patch.object(metric_source.Sonar, 'version_number') as mock_version_number:
            mock_version_number.return_value = '6.3'
            sonar = metric_source.Sonar('http://sonar/')
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        product = domain.Product()
        self.assertEqual(dict(), SonarMetric(product, project).url())
