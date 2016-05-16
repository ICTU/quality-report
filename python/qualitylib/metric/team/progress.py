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


from ..metric_source_mixin import BirtMetricMixin
from ..quality_attributes import PROGRESS
from ...domain import LowerIsBetterMetric
from ... import metric_source


class TeamProgress(BirtMetricMixin, LowerIsBetterMetric):
    """ Metric for measuring the progress of a team. """

    name = 'Team voortgang'
    norm_template = 'De vereiste velocity om het sprintdoel te halen is lager dan of gelijk aan {target_factor:.1f} ' \
        'maal de geplande velocity. Als de velocity die nodig is om het sprintdoel te halen hoger wordt dan ' \
        '{low_target_factor:.1f} maal de geplande velocity is deze metriek rood.'
    template = 'Team {name} heeft een velocity van {value:.1f} punt per dag nodig om het sprintdoel van de huidige ' \
        'sprint ({sprint_goal:.1f} punten) te halen. De geplande velocity is {planned_velocity:.1f} punt per dag. ' \
        'De tot nu toe (dag {sprint_day} van {sprint_length}) gerealiseerde velocity is {actual_velocity:.1f} ' \
        'punt per dag ({actual_points:.1f} punten).'
    quality_attribute = PROGRESS
    target_factor = 1.25
    low_target_factor = 1.5
    metric_source_classes = (metric_source.Birt,)

    @classmethod
    def can_be_measured(cls, team, project):
        return super(TeamProgress, cls).can_be_measured(team, project) and team.is_scrum_team()

    @classmethod
    def norm_template_default_values(cls):
        values = super(TeamProgress, cls).norm_template_default_values()
        values['target_factor'] = cls.target_factor
        values['low_target_factor'] = cls.low_target_factor
        return values

    def __init__(self, *args, **kwargs):
        super(TeamProgress, self).__init__(*args, **kwargs)
        self.__birt_team_id = self._subject.metric_source_id(self._birt)
        planned_velocity = self._birt.planned_velocity(self.__birt_team_id)
        self.target_value = planned_velocity * self.target_factor
        self.low_target_value = planned_velocity * self.low_target_factor

    def value(self):
        return self._birt.required_velocity(self.__birt_team_id)

    def url(self):
        return dict(Birt=self._birt.sprint_progress_url(self.__birt_team_id))

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(TeamProgress, self)._parameters()
        birt_team_id = self.__birt_team_id
        birt = self._birt
        parameters['sprint_goal'] = birt.nr_points_planned(birt_team_id)
        parameters['actual_points'] = birt.nr_points_realized(birt_team_id)
        parameters['actual_velocity'] = birt.actual_velocity(birt_team_id)
        parameters['planned_velocity'] = birt.planned_velocity(birt_team_id)
        parameters['sprint_length'] = birt.days_in_sprint(birt_team_id)
        parameters['sprint_day'] = birt.day_in_sprint(birt_team_id)
        parameters['target_factor'] = self.target_factor
        parameters['low_target_factor'] = self.low_target_factor
        return parameters
