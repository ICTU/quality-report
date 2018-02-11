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


import datetime
from typing import Optional

from hqlib.typing import MetricParameters, MetricValue, DateTime
from ... import metric_source
from ...domain import LowerIsBetterMetric


class TeamAbsence(LowerIsBetterMetric):
    """ Metric for measuring the number of consecutive days that multiple team members are absent. """

    name = 'Absentie'
    unit = 'werkdagen'
    norm_template = 'Het aantal aaneengesloten {unit} na {start_date} dat meerdere teamleden tegelijk gepland ' \
        'afwezig zijn is lager dan {target} {unit}. Meer dan {low_target} {unit} is rood. Het team bestaat uit {team}.'
    template = 'De langste periode na {start_date} dat meerdere teamleden tegelijk gepland afwezig zijn is ' \
               '{value} {unit} ({start} tot en met {end}). Afwezig zijn: {absentees}.'
    perfect_template = 'Er zijn geen teamleden tegelijk gepland afwezig.'
    target_value = 5
    low_target_value = 10
    metric_source_class = metric_source.HolidayPlanner

    @classmethod
    def norm_template_default_values(cls) -> MetricParameters:
        values = super(TeamAbsence, cls).norm_template_default_values()
        values['team'] = '(Lijst van teamleden)'
        values['start_date'] = 'vandaag'
        return values

    def value(self) -> MetricValue:
        return self._metric_source.days(self._subject, start_date=self.__start_date())[0] if self._metric_source else -1

    def is_applicable(self) -> bool:
        return len(self._subject.members()) > 1

    def _parameters(self) -> MetricParameters:
        # pylint: disable=protected-access
        parameters = super()._parameters()
        parameters['team'] = ', '.join(sorted([member.name() for member in self._subject.members()]))
        parameters['start_date'] = str(self.__start_date() or 'vandaag')
        if self._metric_source:
            length, start, end, members = self._metric_source.days(self._subject)
            if length:
                parameters['start'] = start.isoformat()
                parameters['end'] = end.isoformat()
                parameters['absentees'] = ', '.join(sorted([member.name() for member in members]))
        return parameters

    def __start_date(self) -> Optional[DateTime]:
        """ Return the date from which to start monitoring. """
        start_date = self._subject.metric_options(self.__class__).get('start_date')
        return start_date if start_date and start_date > datetime.date.today() else None
