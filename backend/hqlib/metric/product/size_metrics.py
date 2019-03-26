"""
Copyright 2012-2019 Ministerie van Sociale Zaken en Werkgelegenheid

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

from typing import List

from hqlib.typing import MetricParameters, MetricValue
from ..metric_source_mixin import SonarMetric, SonarDashboardMetric
from ...domain import LowerIsBetterMetric, Product


class ProductLOC(SonarDashboardMetric, LowerIsBetterMetric):
    """ Metric for measuring the size (in number of lines of code) of a product. """

    name = 'Component omvang'
    unit = 'regels code'
    target_value = 5000
    low_target_value = 6000

    def value(self) -> MetricValue:
        return self._metric_source.ncloc(self._sonar_id()) if self._metric_source else -1


class TotalLOC(SonarMetric, LowerIsBetterMetric):
    """ Metric for measuring the total size (in number of lines of code) of several products. """

    name = 'Totale omvang'
    unit = 'regels code'
    template = 'Het totaal aantal {unit} voor de producten {products} is {value} {unit}.'
    target_value = 30000
    # Maximum number of LOC to be eligible for 4 stars, see
    # https://www.softwareimprovementgroup.com/wp-content/uploads/2018/05/20180509-SIG-TUViT-Evaluation-Criteria-Trusted-Product-Maintainability-Guidance-for-producers.pdf
    # We use the lowest number (Python; 122000 LOC in 20 years = 30500 in 5 years)
    low_target_value = 30500

    def _parameters(self) -> MetricParameters:
        parameters = super()._parameters()
        products = self.__main_products()
        parameters['products'] = ', '.join([product.name() for product in products])
        return parameters

    def value(self) -> MetricValue:
        if not self._metric_source:
            return -1
        total = 0
        for product in self.__main_products():
            sonar_id = product.metric_source_id(self._metric_source)
            if sonar_id:
                product_size = self._metric_source.ncloc(sonar_id)
                if product_size == -1:
                    return -1
                total += product_size
        return total

    def recent_history(self) -> List[int]:
        """ Subtract the minimum value from all values so that we can send more data to the Google Chart API. """
        historic_values = [h for h in super().recent_history() if h is not None]
        minimum_value = min(historic_values) if historic_values else 0
        return [value - minimum_value for value in historic_values]

    def __main_products(self) -> List[Product]:
        """ Return the main products. """
        return [product for product in self._project.products() if product.is_main()]
