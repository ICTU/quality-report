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


from .alerts_metrics import AlertsMetric
from ... import metric_source


class ZAPScanAlertsMetric(AlertsMetric):
    """ Base class for metrics that measure the number of ZAP Scan alerts with a certain risk level. """

    unit = 'security waarschuwingen'
    norm_template = 'Het product heeft geen {risk_level} risico ZAP Scan {unit}. ' \
                    'Meer dan {low_target} is rood.'
    metric_source_class = metric_source.ZAPScanReport

    extra_info_headers = {
        "title": "Waarschuwing",
        "url": "Locatie",
        "warning_id": "False-positive",
    }

    def extra_info_rows(self) -> list:
        """ Returns warnings info tuple as rows of extra info table. """
        return self._metric_source.get_warnings_info(self.risk_level_key, *self._metric_source_urls())


class HighRiskZAPScanAlertsMetric(ZAPScanAlertsMetric):
    """ Metric for measuring the number of high risk ZAP Scan alerts. """

    name = 'Hoeveelheid ZAP Scan waarschuwingen met hoog risiconiveau'
    risk_level = 'hoog'
    risk_level_key = 'high'
    low_target_value = 3
    url_label_text = "Waarschuwingen met hoog risiconiveau"


class MediumRiskZAPScanAlertsMetric(ZAPScanAlertsMetric):
    """ Metric for measuring the number of medium risk ZAP Scan alerts. """

    name = 'Hoeveelheid ZAP Scan waarschuwingen met medium risiconiveau'
    risk_level = 'medium'
    risk_level_key = 'medium'
    low_target_value = 10
    url_label_text = "Waarschuwingen met medium risiconiveau"
