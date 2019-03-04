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

from hqlib import utils
from hqlib.typing import MetricParameters, MetricValue
from ..metric_source_mixin import SonarDashboardMetric, SonarMetric
from ...domain import LowerIsBetterMetric
from ...metric_source import OJAuditReport


class Violations(SonarDashboardMetric, LowerIsBetterMetric):
    """ Metric for measuring the amount of violations reported by Sonar. """
    unit = 'violations'
    norm_template = 'Maximaal {target} {violation_type} {unit}. ' \
        'Meer dan {low_target} {violation_type} {unit} is rood.'
    template = '{name} heeft {value} {violation_type} {unit}.'
    violation_type = 'Subclass responsibility'

    extra_info_headers = {"violation_type": "Violation type",
                          "number": "Aantal__detail-column-number",
                          "debt": "Geschatte oplostijd__detail-column-number"}

    def extra_info_rows(self) -> List:
        """ Returns formatted rows of extra info table for code maintainability metrics. """
        violation_sorts = [('BUG', 'Bugs'), ('VULNERABILITY', 'Vulnerabilities'), ('CODE_SMELL', 'Code Smell')]
        ret = list()
        for sort in violation_sorts:
            url, count, effort = \
                self._metric_source.violations_type_severity(self._metric_source_id, sort[0], self.violation_type)

            ret.append((utils.format_link_object(url, sort[1]), count, effort))
        return ret

    @classmethod
    def norm_template_default_values(cls):
        values = super(Violations, cls).norm_template_default_values()
        values['violation_type'] = cls.violation_type
        return values

    def value(self) -> MetricValue:
        method_name = '{0}_violations'.format(self.violation_type)
        val = getattr(self._metric_source, method_name)(self._sonar_id()) if self._metric_source else -1
        if val <= 0:
            self.extra_info_headers = None
        return val

    def _parameters(self) -> MetricParameters:
        # pylint: disable=protected-access
        parameters = super()._parameters()
        parameters['violation_type'] = self.violation_type
        return parameters


class BlockerViolations(Violations):
    """ Metric for measuring the number of blocker violations reported by Sonar. """

    name = 'Hoeveelheid blocker violations'
    violation_type = 'blocker'
    target_value = 0
    low_target_value = 0
    url_label_text = 'Blocker violations per soort'


class CriticalViolations(Violations):
    """ Metric for measuring the number of critical violations reported by Sonar. """

    name = 'Hoeveelheid critical violations'
    violation_type = 'critical'
    target_value = 0
    low_target_value = 1
    url_label_text = 'Critical violations per soort'


class MajorViolations(Violations):
    """ Metric for measuring the number of major violations reported by Sonar. """

    name = 'Hoeveelheid major violations'
    violation_type = 'major'
    target_value = 25
    low_target_value = 50
    url_label_text = 'Major violations per soort'


class ViolationSuppressions(SonarMetric, LowerIsBetterMetric):
    """ Metric for measuring the number of violations suppressed. """
    name = "Hoeveelheid onderdrukte violations"
    unit = "onderdrukte violations"
    norm_template = "Maximaal {target} {unit}. Meer dan {low_target} {unit} is rood."
    template = "{name} heeft {value} {unit}."
    target_value = 25
    low_target_value = 50
    extra_info_headers = {"suppression_type": "Wijze van onderdrukking",
                          "number": "Aantal__detail-column-number"}

    def value(self) -> MetricValue:
        if not self._metric_source:
            return -1
        counts = [suppression[0] for suppression in self._suppressions()]
        return -1 if -1 in counts else sum(counts)

    def _metric_source_urls(self) -> List[str]:
        """ Return the url to the suppressed violations. """
        # This should ideally link to an issue search that returns all violation suppressions, but that doesn't
        # seem to be possible in SonarQube
        return [self._metric_source.violations_url(self._sonar_id())] if self._metric_source else []

    def extra_info_rows(self) -> List:
        """ Returns formatted rows of extra info table for code maintainability metrics. """
        if not self._metric_source:
            return []
        rows = list()
        for count, url, label in self._suppressions():
            if count == -1:
                return []
            rows.append((utils.format_link_object(url, label), count))
        return rows

    def _suppressions(self) -> List:
        """ Return the violation suppressions. """
        sonar, sonar_id = self._metric_source, self._sonar_id()
        return [
            (sonar.false_positives(sonar_id), sonar.false_positives_url(sonar_id),
             "Gemarkeerd als false positive in SonarQube"),
            (sonar.wont_fix(sonar_id), sonar.wont_fix_url(sonar_id),
             "Gemarkeerd als won't fix in SonarQube"),
            (sonar.suppressions(sonar_id), sonar.suppressions_url(sonar_id),
             "Gemarkeerd in de broncode met annotatie, commentaar (bijv. //NOSONAR) of pragma")]


class OJAuditViolations(LowerIsBetterMetric):
    """ Base class for OJAudit metrics. """
    unit = 'violations'
    norm_template = 'Maximaal {target} {violation_type} {unit}. ' \
        'Meer dan {low_target} {violation_type} {unit} is rood.'
    template = '{name} heeft {value} {violation_type} {unit}.'
    violation_type = 'Subclass responsibility'
    metric_source_class = OJAuditReport

    @classmethod
    def norm_template_default_values(cls):
        values = super(OJAuditViolations, cls).norm_template_default_values()
        values['violation_type'] = cls.violation_type
        return values

    def value(self) -> MetricValue:
        return self._metric_source.violations(self.violation_type, *self._get_metric_source_ids()) \
            if self._metric_source else -1

    def _parameters(self) -> MetricParameters:
        # pylint: disable=protected-access
        parameters = super()._parameters()
        parameters['violation_type'] = self.violation_type
        return parameters


class OJAuditWarnings(OJAuditViolations):
    """ OJ Audit warnings metric. """
    name = 'Hoeveelheid OJ Audit warnings'
    violation_type = 'warning'
    target_value = 10
    low_target_value = 50


class OJAuditErrors(OJAuditViolations):
    """ OJ Audit errors metric. """
    name = 'Hoeveelheid OJ Audit errors'
    violation_type = 'error'
    target_value = 0
    low_target_value = 10


class OJAuditExceptions(OJAuditViolations):
    """ OJ Audit exceptions metric. """
    name = 'Hoeveelheid OJ Audit exceptions'
    violation_type = 'exception'
    target_value = 0
    low_target_value = 0
