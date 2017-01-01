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

import datetime

from ... import metric_source
from ...domain import Metric


class TeamSpirit(Metric):
    """ Metric for measuring the spirit of a specific team. The team simply picks a smiley. """

    name = 'Team stemming'
    unit = ''
    norm_template = 'De stemming wordt door het team zelf bepaald door het kiezen van een smiley. ' \
        'De norm hierbij is een tevreden team, neutraal is geel, ontevreden is rood. ' \
        'Als de meting ouder is dan {old_age} dagen is de status geel, ouder dan {max_old_age} dagen is rood.'
    template = 'De stemming van team {name} was {value} op {date}.'
    target_value = ':-)'
    perfect_value = ':-)'
    low_target_value = ':-('
    numerical_value_map = {':-(': 0, ':-|': 1, ':-)': 2}
    old_age = datetime.timedelta(days=21)
    max_old_age = 2 * old_age
    metric_source_classes = (metric_source.TeamSpirit,)

    def value(self):
        return self._metric_source.team_spirit(self._metric_source_id) or '?'

    def numerical_value(self):
        return self.numerical_value_map.get(self.value(), -1)

    def y_axis_range(self):
        values = self.numerical_value_map.values()
        return min(values), max(values)

    def _needs_immediate_action(self):
        # First check whether the metric needs immediate action because it was measured too long ago.
        # If not, check whether the spirit is too low.
        return True if super(TeamSpirit, self)._needs_immediate_action() else self.value() == self.low_target()

    def _is_value_better_than(self, target):
        return self.numerical_value() > self.numerical_value_map.get(target, -1)

    def _is_below_target(self):
        # First check whether the metric needs action because it was measured too long ago.
        # If not, check whether the spirit is low.
        return True if super(TeamSpirit, self)._is_below_target() else \
            self.numerical_value() < max(self.numerical_value_map.values())

    def _date(self):
        return self._metric_source.date_of_last_team_spirit_measurement(self._metric_source_id)

    def _missing(self):
        return not self._metric_source.team_spirit(self._metric_source_id)
