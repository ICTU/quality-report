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

from .. import LowerIsBetterMetric
from ..metric_source_mixin import JiraMetricMixin
from ..quality_attributes import PROGRESS, SECURITY
from ... import metric_source


class OpenBugs(JiraMetricMixin, LowerIsBetterMetric):
    """ Metric for measuring the number of open bug reports. """

    name = 'Hoeveelheid open bugreports'
    unit = 'open bugreports'
    norm_template = 'Het aantal {unit} is minder dan {target}. Meer dan {low_target} {unit} is rood.'
    template = 'Het aantal {unit} is {value}.'
    target_value = 50
    low_target_value = 100
    quality_attribute = PROGRESS

    @classmethod
    def can_be_measured(cls, subject, project):
        jira = project.metric_source(metric_source.Jira)
        return super(OpenBugs, cls).can_be_measured(subject, project) and jira.has_open_bugs_query()

    def value(self):
        return self._jira.nr_open_bugs()

    def url(self):
        return {'Jira': self._jira.nr_open_bugs_url()}


class OpenSecurityBugs(JiraMetricMixin, LowerIsBetterMetric):
    """ Metric for measuring the number of open security bugs. """

    name = 'Hoeveelheid open beveiligingsbugreports'
    unit = 'beveiligingsbugreports'
    norm_template = 'Het aantal {unit} met prioriteit major of hoger dat meer dan een ' \
        'sprint open staat is minder dan {target}. Meer dan {low_target} {unit} is rood.'
    template = 'Het aantal {unit} met prioriteit major of hoger dat meer dan een sprint ' \
        'open staat is {value}.'
    target_value = 0
    low_target_value = 3
    quality_attribute = SECURITY

    @classmethod
    def can_be_measured(cls, subject, project):
        jira = project.metric_source(metric_source.Jira)
        return super(OpenSecurityBugs, cls).can_be_measured(subject, project) and jira.has_open_security_bugs_query()

    def value(self):
        return self._jira.nr_open_security_bugs()

    def url(self):
        return {'Jira': self._jira.nr_open_security_bugs_url()}


class TechnicalDebtIssues(JiraMetricMixin, LowerIsBetterMetric):
    """ Metric for measuring the number of technical debt issues. """

    name = 'Hoeveelheid technische schuld issues'
    unit = 'technische schuld issues'
    norm_template = 'Het aantal {unit} is maximaal {target}. Meer dan {low_target} {unit} is rood.'
    template = 'Het aantal {unit} is {value}.'
    target_value = 10
    low_target_value = 50
    quality_attribute = PROGRESS

    @classmethod
    def can_be_measured(cls, subject, project):
        jira = project.metric_source(metric_source.Jira)
        return super(TechnicalDebtIssues, cls).can_be_measured(subject, project) and \
            jira.has_technical_debt_issues_query()

    def value(self):
        return self._jira.nr_technical_debt_issues()

    def url(self):
        return {'Jira': self._jira.nr_technical_debt_issues_url()}
