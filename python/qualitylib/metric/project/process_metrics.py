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

from .. import HigherIsBetterMetric
from ..metric_source_mixin import JiraMetricMixin
from ..quality_attributes import PROGRESS
from ... import metric_source


class ReadyUserStoryPoints(JiraMetricMixin, HigherIsBetterMetric):
    """ Metric for measuring the number of user story points ready. """

    name = 'Ready user story punten'
    norm_template = 'Het aantal ready user story punten is meer dan {target}. Minder dan {low_target} is rood.'
    template = 'Het aantal ready user story punten is {value}.'
    target_value = 10
    low_target_value = 20
    quality_attribute = PROGRESS

    @classmethod
    def can_be_measured(cls, subject, project):
        jira = project.metric_source(metric_source.Jira)
        return super(ReadyUserStoryPoints, cls).can_be_measured(subject, project) and \
            jira.has_user_stories_ready_query()

    def value(self):
        return self._jira.nr_story_points_ready()

    def url(self):
        return {'Jira': self._jira.user_stories_ready_url()}
