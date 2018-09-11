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


import functools
from typing import List, Dict, Tuple, Union
from hqlib.typing import MetricParameters, MetricValue
from ... import metric_source
from ... import utils
from ...domain import HigherIsBetterMetric, LowerIsBetterMetric


class ReadyUserStoryPoints(HigherIsBetterMetric):
    """ Metric for measuring the number of user story points ready. """

    name = 'Hoeveelheid ready user story punten'
    unit = 'ready user story punten'
    target_value = 30
    low_target_value = 15
    metric_source_class = metric_source.ReadyUserStoryPointsTracker
    extra_info_headers = {"issue": "Ready stories", "points": "User story punten__detail-column-number"}
    url_label_text = "Lijst van stories"

    def value(self) -> MetricValue:
        if self._metric_source:
            self._extra_info_data = self._metric_source.issues_with_field(*self._get_metric_source_ids())
            return sum([row[1] for row in self._extra_info_data])
        return -1


class UserStoriesDuration(LowerIsBetterMetric):
    """ Metric for measuring the duration of user stories. """

    name = 'Gemiddelde looptijd van user stories'
    unit = 'dagen gemiddeld in progress'
    norm_template = "User stories zijn " +\
                    LowerIsBetterMetric.norm_template[0].lower() + LowerIsBetterMetric.norm_template[1:]
    template = '{total} user stories waren {value} {unit}.'
    target_value = 7
    low_target_value = 14
    metric_source_class = metric_source.UserStoriesDurationTracker
    url_label_text = 'Gemiddelde looptijd van user stories'
    extra_info_headers = {"story": "Story", "day_in": "Begin uitvoering", "day_out": "Einde uitvoering",
                          "days": "Aantal dagen__detail-column-number", "is_omitted": "_detail-row-alter"}

    @functools.lru_cache(maxsize=1024)
    def value(self) -> MetricValue:
        return round(self._average_duration_of_issues(*self._get_metric_source_ids()), 1) \
            if self._metric_source else -1

    def _average_duration_of_issues(self, *metric_source_ids: str) -> int:
        """ Return the average duration in days the issues were in status 'In Progress'. """
        for query_id in metric_source_ids:
            try:
                self._metric_source.sum_for_all_issues(query_id, self._get_days_in_progress, self._extra_info_data)
            except ValueError:
                return -1  # Error already logged in utils.eval_json
        days = self.__sum_days(self._extra_info_data)
        stories = self.__count_stories(self._extra_info_data)
        return days / stories if stories > 0 else -1

    def _get_days_in_progress(self, issue: Dict) -> Tuple[object, str, str, Union[str, int], bool]:
        """ Fetch the changelog of the given issue and get number of days between it is moved for the first time
            to the status "In Progress", till the last time it is moved out of it. """
        issue_link = utils.format_link_object(
            self._metric_source.get_issue_url(issue['key']), issue['fields']['summary'])
        to_in_progress_date, from_in_progress_date = self._metric_source.get_start_and_end_progress_date(issue)
        to_date_str = utils.format_date(to_in_progress_date, year=True) if to_in_progress_date else 'geen'
        from_date_str = utils.format_date(from_in_progress_date, year=True) if from_in_progress_date else 'geen'
        both_dates_ok = from_in_progress_date and to_in_progress_date
        days = (from_in_progress_date - to_in_progress_date).days if both_dates_ok else "n.v.t"
        yield issue_link, to_date_str, from_date_str, days, not both_dates_ok

    @staticmethod
    def __count_stories(extra_info: List[Tuple]):
        return sum(not t[4] for t in extra_info)

    @staticmethod
    def __sum_days(extra_info: List[Tuple]):
        return sum(t[3] if not t[4] else 0 for t in extra_info)

    def _parameters(self) -> MetricParameters:
        parameters = super()._parameters()
        parameters["total"] = self._metric_source.nr_issues(*self._get_metric_source_ids())[0] \
            if self._metric_source else "?"
        return parameters


class UserStoriesWithNumberOfIssues(LowerIsBetterMetric):
    """ Base class for all metrics that are counting issues. """
    extra_info_headers = {"issue": "Issue"}
    url_label_text = "Lijst van issues"

    @functools.lru_cache(maxsize=1024)
    def value(self) -> MetricValue:
        result = -1
        if self._metric_source:
            result, self._extra_info_data = self._metric_source.nr_issues(
                *self._get_metric_source_ids())
        return result


class UserStoriesInProgress(UserStoriesWithNumberOfIssues):
    """ Metric for measuring the number of user stories in progress in current sprint . """

    name = 'Hoeveelheid user stories in progress'
    unit = 'stories in progress'
    target_value = 3
    low_target_value = 5
    metric_source_class = metric_source.UserStoriesInProgressTracker


class UserStoriesWithoutAssessmentMetric(UserStoriesWithNumberOfIssues):
    """ Metric for measuring the number of user stories without the proper assessment. """

    template = 'Het aantal {unit} is {value}.'
    target_value = 1
    low_target_value = 3
    nr_user_stories_without_risk_assessment = 'Subclass responsibility'


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


class PredictedNumberOfFinishedUserStoryPoints(HigherIsBetterMetric):
    """ Metric for the predicted percentage of user story points the project will deliver in the current sprint. """
    name = "Voorspelling van het percentage user story punten dat in de huidige sprint zal worden opgeleverd"
    unit = "%"
    norm_template = "Het voorspelde aantal user story punten voor de huidige sprint is tenminste {target}{unit} van " \
                    "het geplande aantal user story punten. De metriek is rood als de voorspelling minder dan " \
                    "{low_target}{unit} van het geplande aantal user story punten is."
    template = "Het voorspelde aantal user story punten ({predicted}) voor de huidige sprint is {value}{unit} van " \
               "het geplande aantal user story punten ({planned})."
    metric_source_class = metric_source.UserStoryPointsPredictor
    target_value = 90
    low_target_value = 80

    def value(self) -> MetricValue:
        if not self._metric_source:
            return -1
        prediction = self._metric_source.predicted_number_of_user_story_points(*self._get_metric_source_ids())
        planned = self._metric_source.planned_number_of_user_story_points(*self._get_metric_source_ids())
        if planned == 0 or -1 in (prediction, planned):
            return -1
        return round((prediction / planned) * 100)

    def _parameters(self):
        parameters = super()._parameters()
        if self._metric_source:
            ids = self._get_metric_source_ids()
            parameters["predicted"] = self._metric_source.predicted_number_of_user_story_points(*ids)
            parameters["planned"] = self._metric_source.planned_number_of_user_story_points(*ids)
        return parameters
