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

from hqlib import utils
from ... import metric_source
from .alerts_metrics import AlertsMetric


class CheckmarxAlertsMetric(AlertsMetric):
    """ Base class for metrics that measure the number of Checkmarx alerts with a certain risk level. """

    unit = 'security waarschuwingen'
    norm_template = 'Het product heeft geen {risk_level} risico Checkmarx {unit}. ' \
                    'Meer dan {low_target} is rood.'
    metric_source_class = metric_source.Checkmarx
    extra_info_headers = \
        {"title": "Title", "group": "Groep", "number": "Aantal gevonden__detail-column-number", "state": "Status"}

    def extra_info_rows(self) -> list((object, str, int, str)):
        """ Returns formatted rows of extra info table for checkmarx. """
        self._metric_source.obtain_issues(self._get_metric_source_ids(), self.risk_level_key.title())
        return [(utils.format_link_object(issue.display_url, issue.title), issue.group, issue.count, issue.status)
                for issue
                in self._metric_source.issues()]

    def _nr_alerts(self):
        """ Return the number of warnings. """
        ids = self._get_metric_source_ids()
        return self._metric_source.nr_warnings(tuple(ids), self.risk_level_key) if self._metric_source else -1


class HighRiskCheckmarxAlertsMetric(CheckmarxAlertsMetric):
    """ Metric for measuring the number of high risk Checkmarx alerts. """

    name = 'Hoeveelheid Checkmarx waarschuwingen met hoog risiconiveau'
    url_label_text = "Waarschuwingen met hoog risiconiveau"
    risk_level = 'hoog'
    risk_level_key = 'high'
    low_target_value = 3


class MediumRiskCheckmarxAlertsMetric(CheckmarxAlertsMetric):
    """ Metric for measuring the number of medium risk Checkmarx alerts. """

    name = 'Hoeveelheid Checkmarx waarschuwingen met medium risiconiveau'
    url_label_text = "Waarschuwingen met medium risiconiveau"
    risk_level = 'medium'
    risk_level_key = 'medium'
    low_target_value = 10
