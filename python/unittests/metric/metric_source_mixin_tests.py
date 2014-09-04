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

from qualitylib import metric, domain, metric_source
import unittest


class SonarMetricMixinUnderTest(metric.SonarMetricMixin, metric.Metric):
    ''' Create a testable class by mixing the mixin class with a metric 
        class. '''
    pass


class SonarMetricMixinTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the Sonar metric source mixin class. '''

    def test_can_be_measured(self):
        ''' Test that subclasses of the Sonar metric mixin can be measured
            when the project has Sonar. '''
        project = domain.Project(metric_sources={metric_source.Sonar: 'Sonar'})
        product = domain.Product(project)
        self.failUnless(SonarMetricMixinUnderTest.can_be_measured(product,
                                                                  project))

    def test_cant_be_measured_without_sonar(self):
        ''' Test that subclasses of the Sonar metric mixin can't be measured
            when the product has a Sonar id but the project has no Sonar. '''
        project = domain.Project()
        product = domain.Product(project)
        self.failIf(SonarMetricMixinUnderTest.can_be_measured(product, project))
