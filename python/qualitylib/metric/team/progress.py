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


from ...domain import LowerIsBetterMetric
from ... import metric_source


class TeamProgress(LowerIsBetterMetric):
    """ Metric for measuring the progress of a team. """

    name = 'Team voortgang'
    unit = ''
    norm_template = 'De vereiste velocity om het sprintdoel te halen is lager dan of gelijk aan {target_factor:.1f} ' \
        'maal de geplande velocity. Als de velocity die nodig is om het sprintdoel te halen hoger wordt dan ' \
        '{low_target_factor:.1f} maal de geplande velocity is deze metriek rood.'
    template = 'Team {name} heeft een velocity van {value:.1f} punt per dag nodig om het sprintdoel van de huidige ' \
        'sprint ({sprint_goal:.1f} punten) te halen. De geplande velocity is {planned_velocity:.1f} punt per dag. ' \
        'De tot nu toe (dag {sprint_day} van {sprint_length}) gerealiseerde velocity is {actual_velocity:.1f} ' \
        'punt per dag ({actual_points:.1f} punten).'
    target_factor = 1.25
    low_target_factor = 1.5
    metric_source_classes = (metric_source.Birt,)

    @classmethod
    def norm_template_default_values(cls):
        values = super(TeamProgress, cls).norm_template_default_values()
        values['target_factor'] = cls.target_factor
        values['low_target_factor'] = cls.low_target_factor
        return values

    def __init__(self, *args, **kwargs):
        super(TeamProgress, self).__init__(*args, **kwargs)
        planned_velocity = self._metric_source.planned_velocity(self._metric_source_id) or 0
        self.target_value = planned_velocity * self.target_factor
        self.low_target_value = planned_velocity * self.low_target_factor

    def value(self):
        velocity = self._metric_source.required_velocity(self._metric_source_id)
        return -1 if velocity is None else velocity

    def url(self):
        url = self._metric_source.sprint_progress_url(self._metric_source_id)
        return dict() if url is None else dict(Birt=url)

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(TeamProgress, self)._parameters()
        birt_team_id = self._metric_source_id
        birt = self._metric_source
        parameters['sprint_goal'] = birt.nr_points_planned(birt_team_id)
        parameters['actual_points'] = birt.nr_points_realized(birt_team_id)
        parameters['actual_velocity'] = birt.actual_velocity(birt_team_id)
        parameters['planned_velocity'] = birt.planned_velocity(birt_team_id)
        parameters['sprint_length'] = birt.days_in_sprint(birt_team_id)
        parameters['sprint_day'] = birt.day_in_sprint(birt_team_id)
        parameters['target_factor'] = self.target_factor
        parameters['low_target_factor'] = self.low_target_factor
        return parameters
