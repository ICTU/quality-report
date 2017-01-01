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


class OWASPDependencyWarnings(AlertsMetric):
    """ Base class for metrics that measure the number of external dependencies of the project that have OWASP
        warnings with a certain priority. """

    unit = 'waarschuwingen'
    norm_template = 'Dependencies van het product hebben geen {risk_level} prioriteit OWASP {unit}. ' \
                    'Meer dan {low_target} is rood.'
    template = 'Dependencies van {name} hebben {value} {risk_level} prioriteit {unit}.'
    metric_source_classes = (metric_source.OWASPDependencyReport,)

    def _nr_alerts(self):
        """ Return the number of warnings. """
        ids = self._report_ids()
        return self._metric_source.nr_warnings(ids, self.risk_level_key) if ids else -1

    def _report_ids(self):
        """ Return the Jenkins report ids (job names). """
        if self._metric_source_id is None:
            return []
        else:
            return self._metric_source_id if isinstance(self._metric_source_id, list) else [self._metric_source_id]


class HighPriorityOWASPDependencyWarnings(OWASPDependencyWarnings):
    """ Metric for measuring the number of external dependencies of the project that have high priority OWASP
        warnings. """

    name = 'Hoeveelheid OWASP dependency waarschuwingen met hoge prioriteit'
    risk_level = 'hoge'
    risk_level_key = 'high'
    low_target_value = 3


class NormalPriorityOWASPDependencyWarnings(OWASPDependencyWarnings):
    """ Metric for measuring the number of external dependencies of the project that have high priority OWASP
        warnings. """

    name = 'Hoeveelheid OWASP dependency waarschuwingen met normale prioriteit'
    risk_level = 'normale'
    risk_level_key = 'normal'
    low_target_value = 10
