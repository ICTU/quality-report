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

from ...domain import LowerIsBetterMetric


class AlertsMetric(LowerIsBetterMetric):
    """ Base class for metrics that measure a number of alerts with a certain risk level. """

    template = '{name} heeft {value} {risk_level} risico {unit}.'
    risk_level = risk_level_key = 'Subclass responsibility'
    target_value = 0

    @classmethod
    def norm_template_default_values(cls):
        values = super(AlertsMetric, cls).norm_template_default_values()
        values['risk_level'] = cls.risk_level
        return values

    def value(self):
        return -1 if self._missing() else self._nr_alerts()

    def _missing(self):
        return self._nr_alerts() < 0

    def _nr_alerts(self):
        """ Return the number of alerts. """
        return self._metric_source.alerts(self.risk_level_key, *self._metric_source_urls())

    def _parameters(self):
        parameters = super(AlertsMetric, self)._parameters()
        parameters['risk_level'] = self.risk_level
        return parameters
