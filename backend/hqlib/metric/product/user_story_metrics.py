"""
Copyright 2012-2019 Ministerie van Sociale Zaken en Werkgelegenheid

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


from typing import List, Tuple
from hqlib.typing import MetricParameters
from ...domain import LowerIsBetterMetric
from ...metric_source.abstract.backlog import Backlog


class UserStoryMetric(LowerIsBetterMetric):
    """ Base class for metrics measuring the quality of user stories. """
    unit = 'user stories'
    metric_source_class = Backlog
    extra_info_headers = {"issue": "Issue"}

    def value(self):
        nr_ok_stories, ok_stories = self._nr_user_stories_ok()
        nr_all_stories, all_stories = self._user_stories()
        self._extra_info_data = [el for el in all_stories if el not in ok_stories]
        self.__set_display_url()
        return -1 if -1 in (nr_all_stories, nr_ok_stories) else nr_all_stories - nr_ok_stories

    def __set_display_url(self):
        if self._extra_info_data:
            self._display_url = [issue['href'].rsplit('/', 1)[-1] for issue in self._extra_info_data]

    def _nr_user_stories_ok(self) -> Tuple[int, List[str]]:
        """ Return the number of user stories whose quality is good. """
        raise NotImplementedError

    def _user_stories(self) -> Tuple[int, List[str]]:
        """ Return the total number of user stories. """
        return self._metric_source.nr_user_stories() if self._metric_source else (-1, [])

    def _parameters(self) -> MetricParameters:
        # pylint: disable=protected-access
        parameters = super()._parameters()
        parameters['total'] = self._user_stories()[0]
        return parameters


class UserStoriesNotReviewed(UserStoryMetric):
    """ Metric for measuring the percentage of user stories that not have been reviewed. """

    name = 'Reviewstatus van user stories'
    unit = "niet gereviewde " + UserStoryMetric.unit
    template = 'Er zijn {value} {unit}, van in totaal {total} user stories.'
    target_value = 0
    low_target_value = 5

    def _nr_user_stories_ok(self) -> Tuple[int, List[str]]:
        return self._metric_source.reviewed_user_stories() if self._metric_source else (-1, [])


class UserStoriesNotApproved(UserStoryMetric):
    """ Metric for measuring the number of user stories that not have been approved. """

    name = 'Goedkeuring van user stories'
    unit = "niet goedgekeurde " + UserStoryMetric.unit
    template = 'Er zijn {value} {unit}, van in totaal {total} gereviewde user stories.'
    target_value = 0
    low_target_value = 3

    def _nr_user_stories_ok(self) -> Tuple[int, List[str]]:
        return self._metric_source.approved_user_stories() if self._metric_source else (-1, [])

    def _user_stories(self) -> Tuple[int, List[str]]:
        """ Override the total number of user stories. """
        return self._metric_source.reviewed_user_stories() if self._metric_source else (-1, [])


class UserStoriesWithTooFewLogicalTestCases(UserStoryMetric):
    """ Metric for measuring the number of user stories that has too few logical test cases. """

    name = 'Hoeveelheid logische testgevallen per user story'
    unit = UserStoryMetric.unit + " met onvoldoende logische testgevallen"
    template = 'Er zijn {value} {unit}, van in totaal {total} user stories.'
    target_value = 3
    low_target_value = 5

    def _nr_user_stories_ok(self) -> Tuple[int, List[str]]:
        return self._metric_source.nr_user_stories_with_sufficient_ltcs() if self._metric_source else (-1, [])
