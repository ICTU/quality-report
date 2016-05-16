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

from ..quality_attributes import PROGRESS
from ... import metric_source
from ...domain import LowerIsBetterMetric


class TeamAbsence(LowerIsBetterMetric):
    """ Metric for measuring the number of consecutive days that multiple team members are absent. """

    name = 'Absentie'
    norm_template = 'Het aantal aaneengesloten dagen dat meerdere teamleden tegelijk gepland afwezig zijn is ' \
        'lager dan {target} werkdagen. Meer dan {low_target} werkdagen is rood. Het team bestaat uit {team}.'
    template = 'De langste periode dat meerdere teamleden tegelijk gepland afwezig zijn is {value} werkdagen ' \
        '({start} tot en met {end}). Afwezig zijn: {absentees}.'
    perfect_template = 'Er zijn geen teamleden tegelijk gepland afwezig.'
    target_value = 5
    low_target_value = 10
    quality_attribute = PROGRESS
    metric_source_classes = (metric_source.HolidayPlanner,)

    @classmethod
    def can_be_measured(cls, team, project):
        return super(TeamAbsence, cls).can_be_measured(team, project) and len(team.members()) > 1

    @classmethod
    def norm_template_default_values(cls):
        values = super(TeamAbsence, cls).norm_template_default_values()
        values['team'] = '(Lijst van teamleden)'
        return values

    def __init__(self, *args, **kwargs):
        super(TeamAbsence, self).__init__(*args, **kwargs)
        self.__planner = self._project.metric_source(metric_source.HolidayPlanner)

    def value(self):
        return self.__planner.days(self._subject)[0]

    def url(self):
        return dict(Planner=self.__planner.url())

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(TeamAbsence, self)._parameters()
        parameters['team'] = ', '.join([member.name() for member in self._subject.members()])
        length, start, end, members = self.__planner.days(self._subject)
        if length:
            parameters['start'] = start.isoformat()
            parameters['end'] = end.isoformat()
            parameters['absentees'] = ', '.join(sorted([member.name() for member in members]))
        return parameters

    def _get_template(self):
        # pylint: disable=protected-access
        return self.perfect_template if self._is_perfect() else super(TeamAbsence, self)._get_template()
