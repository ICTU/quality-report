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


from ... import metric_source
from ...domain import HigherIsBetterMetric, LowerIsBetterMetric


class ReadyUserStoryPoints(HigherIsBetterMetric):
    """ Metric for measuring the number of user story points ready. """

    name = 'Hoeveelheid ready user story punten'
    unit = 'ready user story punten'
    norm_template = 'Het aantal {unit} is meer dan {target}. Minder dan {low_target} {unit} is rood.'
    template = 'Het aantal {unit} is {value}.'
    target_value = 30
    low_target_value = 15
    metric_source_class = metric_source.ReadyUserStoryPointsTracker

    def value(self):
        return self._metric_source.sum_field(*self._get_metric_source_ids()) if self._metric_source else -1


class UserStoriesWithoutAssessmentMetric(LowerIsBetterMetric):
    """ Metric for measuring the number of user stories without the proper assessment. """
    norm_template = 'Het aantal {unit} is minder dan {target}. Meer dan {low_target} {unit} is rood.'
    template = 'Het aantal {unit} is {value}.'
    target_value = 1
    low_target_value = 3
    nr_user_stories_without_risk_assessment = 'subclass responsibility'

    def value(self):
        return self._metric_source.nr_issues(*self._get_metric_source_ids()) if self._metric_source else -1


class UserStoriesWithoutSecurityRiskAssessment(UserStoriesWithoutAssessmentMetric):
    """ Metric for measuring the number of user stories without security risk assessment. """

    name = 'Hoeveelheid user stories zonder security risk beoordeling'
    unit = 'ready user stories zonder security risk beoordeling'
    metric_source_class = metric_source.UserStoryWithoutSecurityRiskAssessmentTracker


class UserStoriesWithoutPerformanceRiskAssessment(UserStoriesWithoutAssessmentMetric):
    """ Metric for measuring the number of user stories without performance risk assessment. """

    name = 'Hoeveelheid user stories zonder performance risk beoordeling'
    unit = 'ready user stories zonder performance risk beoordeling'
    metric_source_class = metric_source.UserStoryWithoutPerformanceRiskAssessmentTracker
