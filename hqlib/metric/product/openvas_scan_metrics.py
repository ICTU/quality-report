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

from .alerts_metrics import AlertsMetric
from ... import metric_source


class OpenVASScanAlertsMetric(AlertsMetric):
    """ Base class for metrics that measure the number of Open VAS Scan alerts with a certain risk level. """

    unit = 'waarschuwingen'
    norm_template = 'De gescande omgevingen hebben geen {risk_level} risico Open VAS Scan {unit}. ' \
                    'Meer dan {low_target} is rood.'
    metric_source_classes = (metric_source.OpenVASScanReport,)


class HighRiskOpenVASScanAlertsMetric(OpenVASScanAlertsMetric):
    """ Metric for measuring the number of high risk Open VAS Scan alerts. """

    name = 'Hoeveelheid Open VAS Scan waarschuwingen met hoog risiconiveau'
    risk_level = 'hoog'
    risk_level_key = 'high'
    low_target_value = 3


class MediumRiskOpenVASScanAlertsMetric(OpenVASScanAlertsMetric):
    """ Metric for measuring the number of medium risk Open VAS Scan alerts. """

    name = 'Hoeveelheid Open VAS Scan waarschuwingen met medium risiconiveau'
    risk_level = 'medium'
    risk_level_key = 'medium'
    low_target_value = 10
