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

from ..metric_source_mixin import SonarMetricMixin, SonarDashboardMetricMixin
from ..quality_attributes import SIZE
from ... import metric_info
from ...domain import LowerIsBetterMetric


class ProductLOC(SonarDashboardMetricMixin, LowerIsBetterMetric):
    """ Metric for measuring the size (in number of lines of code) of a product. """

    name = 'Component omvang'
    norm_template = 'Maximaal {target} regels (Java) code.'
    template = '{name} heeft {value} regels code.'
    target_value = 50000
    low_target_value = 100000
    quality_attribute = SIZE

    def value(self):
        return self._sonar.ncloc(self._sonar_id())


class TotalLOC(SonarMetricMixin, LowerIsBetterMetric):
    """ Metric for measuring the total size (in number of lines of code) of several products. """

    name = 'Totale omvang'
    norm_template = 'Maximaal {target} regels (Java) code. Meer dan {low_target} regels (Java) code ' \
        '(herbouwtijd 30 jaar) is rood.'
    template = 'Het totaal aantal LOC voor de producten {products} is {value} regels code.'
    target_value = 160000
    # Maximum number of LOC Java to be eligible for 4 stars, see
    # http://www.sig.eu/nl/diensten/Software%20Product%20Certificering/Evaluation%20Criteria/
    low_target_value = 175000
    quality_attribute = SIZE

    def _parameters(self):
        parameters = super(TotalLOC, self)._parameters()
        products = self.__main_products()
        parameters['products'] = ', '.join([product.product_label() for product in products])
        return parameters

    def value(self):
        total = 0
        for product in self.__main_products():
            sonar_id = metric_info.SonarProductInfo(self._sonar, product).sonar_id()
            if sonar_id:
                total += self._sonar.ncloc(sonar_id)
        return total

    def recent_history(self):
        """ Subtract the minimum value from all values so that we can send more data to the Google Chart API. """
        historic_values = super(TotalLOC, self).recent_history()
        minimum_value = min(historic_values) if historic_values else 0
        return [value - minimum_value for value in historic_values]

    def __main_products(self):
        """ Return the main products. """
        return [product for product in self._project.products() if product.is_main()]
