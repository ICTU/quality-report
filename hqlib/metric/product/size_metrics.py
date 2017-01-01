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
from __future__ import absolute_import

from ..metric_source_mixin import SonarMetricMixin, SonarDashboardMetricMixin
from ... import metric_info
from ...domain import LowerIsBetterMetric


class ProductLOC(SonarDashboardMetricMixin, LowerIsBetterMetric):
    """ Metric for measuring the size (in number of lines of code) of a product. """

    name = 'Component omvang'
    unit = 'regels code'
    norm_template = 'Maximaal {target} {unit}.'
    template = '{name} heeft {value} {unit}.'
    target_value = 50000
    low_target_value = 100000

    def value(self):
        loc = self._metric_source.ncloc(self._sonar_id())
        return -1 if loc is None else loc


class TotalLOC(SonarMetricMixin, LowerIsBetterMetric):
    """ Metric for measuring the total size (in number of lines of code) of several products. """

    name = 'Totale omvang'
    unit = 'regels code'
    norm_template = 'Maximaal {target} {unit}. Meer dan {low_target} {unit} (herbouwtijd 30 jaar) is rood.'
    template = 'Het totaal aantal {unit} voor de producten {products} is {value} {unit}.'
    target_value = 160000
    # Maximum number of LOC Java to be eligible for 4 stars, see
    # http://www.sig.eu/nl/diensten/Software%20Product%20Certificering/Evaluation%20Criteria/
    low_target_value = 175000

    def _parameters(self):
        parameters = super(TotalLOC, self)._parameters()
        products = self.__main_products()
        parameters['products'] = ', '.join([product.name() for product in products])
        return parameters

    def value(self):
        total = 0
        for product in self.__main_products():
            sonar_id = metric_info.SonarProductInfo(self._metric_source, product).sonar_id()
            if sonar_id:
                total += self._metric_source.ncloc(sonar_id)
        return total

    def recent_history(self):
        """ Subtract the minimum value from all values so that we can send more data to the Google Chart API. """
        historic_values = super(TotalLOC, self).recent_history()
        minimum_value = min(historic_values) if historic_values else 0
        return [value - minimum_value for value in historic_values]

    def __main_products(self):
        """ Return the main products. """
        return [product for product in self._project.products() if product.is_main()]
