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

import unittest

from hqlib import metric, domain, metric_source


class FakeBirt(object):
    """ Provide for a fake Birt object. """

    metric_source_name = metric_source.Birt.metric_source_name
    needs_metric_source_id = metric_source.Birt.needs_metric_source_id

    def __init__(self):
        self.down = False

    @staticmethod
    def approved_user_stories():
        """ Return the number of approved user stories. """
        return 20

    def reviewed_user_stories(self):
        """ Return the number of reviewed user stories. """
        return -1 if self.down else 23

    def nr_user_stories(self):
        """ Return the total number of user stories. """
        return -1 if self.down else 25

    @staticmethod
    def nr_user_stories_with_sufficient_ltcs():
        """ Return the number of user stories with enough logical test cases. """
        return 23

    @staticmethod
    def whats_missing_url():
        """ Return the url for the what's missing report. """
        return 'http://whats_missing'


class FakeSubject(object):
    """ Provide for a fake subject. """
    version = ''

    def __init__(self, birt_id=True):
        self.__birt_id = birt_id

    @staticmethod
    def name():
        """ Return the name of the subject. """
        return 'FakeSubject'

    def metric_source_id(self, metric_src):  # pylint: disable=unused-argument
        """ Return the metric source id of the subject for the metric source. """
        return 'birt id' if self.__birt_id else ''


class UserStoriesNotReviewedTest(unittest.TestCase):
    """ Unit tests for the user stories that are not reviewed. """
    def setUp(self):
        self.__birt = FakeBirt()
        self.__subject = FakeSubject()
        self.__project = domain.Project(metric_sources={metric_source.Birt: self.__birt})
        self.__metric = metric.UserStoriesNotReviewed(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric is the number of not reviewed user stories as reported by Birt. """
        self.assertEqual(2, self.__metric.value())

    def test_value_on_error(self):
        """ Test that the value is -1 when the metric source is down. """
        self.__birt.down = True
        self.assertEqual(-1, self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual('FakeSubject heeft 2 niet gereviewde user stories van in totaal 25 user stories.',
                         self.__metric.report())

    def test_url(self):
        """ Test the url is correct. """
        self.assertEqual({FakeBirt.metric_source_name: FakeBirt.whats_missing_url()}, self.__metric.url())


class UserStoriesNotApprovedTest(unittest.TestCase):
    """ Unit tests for the user stories that are not approved. """
    def setUp(self):
        birt = FakeBirt()
        self.__subject = FakeSubject()
        self.__project = domain.Project(metric_sources={metric_source.Birt: birt})
        self.__metric = metric.UserStoriesNotApproved(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric is the number of not approved user stories as reported by Birt. """
        self.assertEqual(3, self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual('FakeSubject heeft 3 niet goedgekeurde user stories van in totaal 23 gereviewde user stories.',
                         self.__metric.report())

    def test_url(self):
        """ Test the url is correct. """
        self.assertEqual({FakeBirt.metric_source_name: FakeBirt.whats_missing_url()}, self.__metric.url())


class UserStoriesWithEnoughLTCsTest(unittest.TestCase):
    """ Unit tests for the user-stories-with-enough-logical-test-cases-metric. """
    def setUp(self):
        self.__birt = FakeBirt()
        self.__subject = FakeSubject()
        self.__project = domain.Project(metric_sources={metric_source.Birt: self.__birt})
        self.__metric = metric.UserStoriesWithTooFewLogicalTestCases(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric is the number of user stories that has too few logical test cases
            as reported by Birt. """
        self.assertEqual(2, self.__metric.value())

    def test_url(self):
        """ Test the url is correct. """
        self.assertEqual({FakeBirt.metric_source_name: self.__birt.whats_missing_url()}, self.__metric.url())
