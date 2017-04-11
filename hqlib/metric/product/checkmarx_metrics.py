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


from .alerts_metrics import AlertsMetric
from ... import metric_source


class CheckmarxAlertsMetric(AlertsMetric):
    """ Base class for metrics that measure the number of Checkmarx alerts with a certain risk level. """

    unit = 'security waarschuwingen'
    norm_template = 'Het product heeft geen {risk_level} risico Checkmarx {unit}. ' \
                    'Meer dan {low_target} is rood.'
    metric_source_class = metric_source.Checkmarx

    def _nr_alerts(self):
        """ Return the number of warnings. """
        ids = self._get_metric_source_ids()
        return self._metric_source.nr_warnings(tuple(ids), self.risk_level_key) if ids else -1


class HighRiskCheckmarxAlertsMetric(CheckmarxAlertsMetric):
    """ Metric for measuring the number of high risk Checkmarx alerts. """

    name = 'Hoeveelheid Checkmarx waarschuwingen met hoog risiconiveau'
    risk_level = 'hoog'
    risk_level_key = 'high'
    low_target_value = 3


class MediumRiskCheckmarxAlertsMetric(CheckmarxAlertsMetric):
    """ Metric for measuring the number of medium risk Checkmarx alerts. """

    name = 'Hoeveelheid Checkmarx waarschuwingen met medium risiconiveau'
    risk_level = 'medium'
    risk_level_key = 'medium'
    low_target_value = 10
