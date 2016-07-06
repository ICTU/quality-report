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

from ..quality_attributes import SECURITY
from ... import metric_source
from ...domain import LowerIsBetterMetric


class OWASPDependencyWarnings(LowerIsBetterMetric):
    """ Base class for metrics that measure the number of external dependencies of the project that have OWASP
        warnings with a certain priority. """

    unit = 'waarschuwingen'
    priority = priority_key = 'Subclass responsibility'
    norm_template = 'Dependencies van het product hebben geen {priority} prioriteit OWASP {unit}. ' \
                    'Meer dan {low_target} is rood.'
    template = 'Dependencies van {name} hebben {value} {priority} prioriteit {unit}.'
    target_value = 0
    quality_attribute = SECURITY
    metric_source_classes = (metric_source.JenkinsOWASPDependencyReport,)

    @classmethod
    def norm_template_default_values(cls):
        values = super(OWASPDependencyWarnings, cls).norm_template_default_values()
        values['priority'] = cls.priority
        return values

    def __init__(self, *args, **kwargs):
        super(OWASPDependencyWarnings, self).__init__(*args, **kwargs)
        self._jenkins_report = self._project.metric_source(metric_source.JenkinsOWASPDependencyReport)

    def value(self):
        return -1 if self._missing() else self._nr_warnings()

    def url(self):
        jenkins_ids = self._jenkins_ids()
        if len(jenkins_ids) == 1:
            return {'Jenkins OWASP dependency report': self._jenkins_report.report_url(jenkins_ids[0])}
        else:
            urls = {}
            for jenkins_id in jenkins_ids:
                label = 'Jenkins OWASP dependency report {jid}'.format(jid=jenkins_id)
                urls[label] = self._jenkins_report.report_url(jenkins_id)
            return urls

    def _missing(self):
        return self._nr_warnings() < 0

    def _nr_warnings(self):
        """ Return the number of warnings. """
        return self._jenkins_report.nr_warnings(self._jenkins_ids(), self.priority_key)

    def _jenkins_ids(self):
        """ Return the Jenkins report ids (job names). """
        report = self._subject.metric_source_id(self._jenkins_report)
        return report if isinstance(report, list) else [report]

    def _parameters(self):
        parameters = super(OWASPDependencyWarnings, self)._parameters()
        parameters['priority'] = self.priority
        return parameters


class HighPriorityOWASPDependencyWarnings(OWASPDependencyWarnings):
    """ Metric for measuring the number of external dependencies of the project that have high priority OWASP
        warnings. """

    name = 'OWASP dependency waarschuwingen met hoge prioriteit'
    priority = 'hoge'
    priority_key = 'high'
    low_target_value = 3


class NormalPriorityOWASPDependencyWarnings(OWASPDependencyWarnings):
    """ Metric for measuring the number of external dependencies of the project that have high priority OWASP
        warnings. """

    name = 'OWASP dependency waarschuwingen met normale prioriteit'
    priority = 'normale'
    priority_key = 'normal'
    low_target_value = 10
