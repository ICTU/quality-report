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

from qualitylib.domain import LowerIsBetterMetric
from qualitylib.metric.metric_source_mixin import SonarMetricMixin, \
    SonarDashboardMetricMixin
from qualitylib.metric.quality_attributes import SIZE


class ProductLOC(SonarDashboardMetricMixin, LowerIsBetterMetric):
    ''' Metric for measuring the size (in number of lines of code) of a
        product. '''

    name = 'Component omvang'
    norm_template = 'Maximaal %(target)d regels (Java) code.'
    template = '%(name)s heeft %(value)d regels code.'
    target_value = 50000
    low_target_value = 100000
    quality_attribute = SIZE

    @classmethod
    def can_be_measured(cls, product, project):
        return super(ProductLOC, cls).can_be_measured(product, project) and \
            product.sonar_id()

    def value(self):
        return self._sonar.ncloc(self._sonar_id())


class TotalLOC(SonarMetricMixin, LowerIsBetterMetric):
    ''' Metric for measuring the total size (in number of lines of code) of
        several products. '''

    name = 'Totale omvang'
    norm_template = 'Maximaal %(target)d regels (Java) code. Meer dan ' \
        '%(low_target)s regels (Java) code (herbouwtijd 30 jaar) is rood.'
    template = 'Het totaal aantal LOC voor alle producten is %(value)d ' \
        'regels code.'
    target_value = 160000
    # Maximum number of LOC Java to be eligible for 4 stars, see
    # http://www.sig.eu/nl/diensten/Software%20Product%20Certificering/Evaluation%20Criteria/  # pylint: disable=C0301
    low_target_value = 175000
    quality_attribute = SIZE

    def value(self):
        total = 0
        for product in self._subject:
            total += self._sonar.ncloc(product.sonar_id())
        return total

    def recent_history(self):
        ''' Subtract the minimum value from all values so that we can send
            more data to the Google Chart API. '''
        historic_values = super(TotalLOC, self).recent_history()
        minimum_value = min(historic_values) if historic_values else 0
        return [value - minimum_value for value in historic_values]
