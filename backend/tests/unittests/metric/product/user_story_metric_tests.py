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

import unittest
from unittest.mock import MagicMock

from hqlib import metric, domain, metric_source


class UserStoriesNotReviewedTest(unittest.TestCase):
    """ Unit tests for the user stories that are not reviewed. """
    def setUp(self):
        self.__birt = MagicMock()
        self.__subject = MagicMock()
        self.__project = domain.Project(metric_sources={metric_source.Backlog: self.__birt})
        self.__metric = metric.UserStoriesNotReviewed(subject=self.__subject, project=self.__project)

    def test_norm(self):
        """ Test that the norm is correct. """
        self.__subject.target.return_value = 0
        self.__subject.low_target.return_value = 5
        self.__birt.nr_user_stories.return_value = -1, []
        self.__birt.reviewed_user_stories.return_value = -1, []
        self.assertEqual("Maximaal 0 niet gereviewde user stories. Meer dan 5 niet gereviewde user stories is rood.",
                         self.__metric.norm())

    def test_value(self):
        """ Test that the value of the metric is the number of not reviewed user stories as reported by Birt. """
        self.__birt.nr_user_stories.return_value = 25, [{"href": "http://aa", "text": "aa"},
                                                        {"href": "http://aa", "text": "bb"}]
        self.__birt.reviewed_user_stories.return_value = 23, [{"href": "http://aa", "text": "aa"}]
        self.assertEqual(2, self.__metric.value())
        self.assertEqual([{"href": "http://aa", "text": "bb"}], self.__metric.extra_info_rows())

    def test_value_on_error(self):
        """ Test that the value is -1 when the metric source is down. """
        self.__birt.nr_user_stories.return_value = 25, []
        self.__birt.reviewed_user_stories.return_value = -1, []
        self.assertEqual(-1, self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.__birt.nr_user_stories.return_value = 25, []
        self.__birt.reviewed_user_stories.return_value = 23, []
        self.assertEqual('Er zijn 2 niet gereviewde user stories, van in totaal 25 user stories.',
                         self.__metric.report())


class UserStoriesNotApprovedTest(unittest.TestCase):
    """ Unit tests for the user stories that are not approved. """
    def setUp(self):
        self.__birt = MagicMock()
        self.__subject = MagicMock()
        self.__project = domain.Project(metric_sources={metric_source.Backlog: self.__birt})
        self.__metric = metric.UserStoriesNotApproved(subject=self.__subject, project=self.__project)

    def test_norm(self):
        """ Test that the norm is correct. """
        self.__subject.target.return_value = 0
        self.__subject.low_target.return_value = 3
        self.__birt.reviewed_user_stories.return_value = -1, []
        self.__birt.approved_user_stories.return_value = -1, []
        self.assertEqual("Maximaal 0 niet goedgekeurde user stories. "
                         "Meer dan 3 niet goedgekeurde user stories is rood.", self.__metric.norm())

    def test_value(self):
        """ Test that the value of the metric is the number of not approved user stories as reported by Birt. """
        self.__birt.approved_user_stories.return_value = 20, [{"href": "http://aa", "text": "aa"}]
        self.__birt.reviewed_user_stories.return_value = 23, [{"href": "http://aa", "text": "aa"},
                                                              {"href": "http://aa", "text": "bb"}]
        self.assertEqual(3, self.__metric.value())
        self.assertEqual([{"href": "http://aa", "text": "bb"}], self.__metric.extra_info_rows())

    def test_report(self):
        """ Test that the report is correct. """
        self.__birt.approved_user_stories.return_value = 20, []
        self.__birt.reviewed_user_stories.return_value = 23, []
        self.assertEqual('Er zijn 3 niet goedgekeurde user stories, van in totaal 23 gereviewde user stories.',
                         self.__metric.report())


class UserStoriesWithEnoughLTCsTest(unittest.TestCase):
    """ Unit tests for the user-stories-with-enough-logical-test-cases-metric. """
    def setUp(self):
        self.__birt = MagicMock()
        self.__subject = MagicMock()
        self.__project = domain.Project(metric_sources={metric_source.Backlog: self.__birt})
        self.__metric = metric.UserStoriesWithTooFewLogicalTestCases(subject=self.__subject, project=self.__project)

    def test_norm(self):
        """ Test that the norm is correct. """
        self.__subject.target.return_value = 3
        self.__subject.low_target.return_value = 5
        self.__birt.nr_user_stories.return_value = -1, []
        self.__birt.nr_user_stories_with_sufficient_ltcs.return_value = -1, []
        self.assertEqual("Maximaal 3 user stories met onvoldoende logische testgevallen. "
                         "Meer dan 5 user stories met onvoldoende logische testgevallen is rood.", self.__metric.norm())

    def test_value(self):
        """ Test that the value of the metric is the number of user stories that has too few logical test cases
            as reported by Birt. """
        self.__birt.nr_user_stories.return_value = 25, [{"href": "http://aa", "text": "aa"},
                                                        {"href": "http://aa", "text": "bb"}]
        self.__birt.nr_user_stories_with_sufficient_ltcs.return_value = 23, [{"href": "http://aa", "text": "aa"}]
        result = self.__metric.value()
        self.assertEqual(2, result)
        self.assertEqual([{"href": "http://aa", "text": "bb"}], self.__metric.extra_info_rows())

    def test_report(self):
        """ Test that the report is correct. """
        self.__birt.nr_user_stories.return_value = 25, []
        self.__birt.nr_user_stories_with_sufficient_ltcs.return_value = 23, []
        self.assertEqual("Er zijn 2 user stories met onvoldoende logische testgevallen, "
                         "van in totaal 25 user stories.", self.__metric.report())
