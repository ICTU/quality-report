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
import unittest

from unittest.mock import patch, MagicMock
from typing import List
from hqlib import metric, domain, metric_source


class FakeBoard(metric_source.TrelloBoard):
    """ Fake a Trello board. """
    ignored = []

    def __init__(self):
        super().__init__('appkey', 'token')

    # pylint: disable=unused-argument

    @staticmethod
    def url(*args):
        """ Return a fake url. """
        return 'http://trello/board'

    @staticmethod
    def datetime(*args):
        """ Fake the date of the last update. """
        return datetime.datetime.now() - datetime.timedelta(minutes=1)

    @staticmethod
    def nr_of_over_due_cards(*args):
        """ Fake the number. """
        return 5

    @staticmethod
    def nr_of_inactive_cards(*args):
        """ Fake the number. """
        return 4

    def ignored_lists(self) -> List[str]:
        """ Return a fake list name. """
        return self.ignored


class UnreachableBoard(FakeBoard):
    """ Pretend that Trello is down. """

    # pylint: disable=unused-argument

    @staticmethod
    def url(*args):
        """ Return a fake url. """
        return 'http://trello.com'

    @staticmethod
    def datetime(*args):
        """ Fake that Trello is down. """
        return datetime.datetime.min

    @staticmethod
    def nr_of_over_due_cards(*args):
        """ Fake that Trello is down. """
        return -1

    @staticmethod
    def nr_of_inactive_cards(*args):
        """ Fake that Trello is down. """
        return -1


class RiskLogTest(unittest.TestCase):
    """ Unit tests for the risk log metric. """

    def setUp(self):
        self.__board = FakeBoard()
        self.__project = domain.Project(
            metric_sources={metric_source.RiskLog: self.__board},
            metric_source_ids={self.__board: 'board_id'})
        self.__metric = metric.RiskLog(project=self.__project, subject=self.__project)

    def test_url(self):
        """ Test that the url of the metric uses the url of the risk log board. """
        self.assertEqual({FakeBoard.metric_source_name: FakeBoard().url()}, self.__metric.url())

    def test_value(self):
        """ Test that the value is the number of days since the last update. """
        self.assertEqual(0, self.__metric.value())

    def test_value_without_metric_source(self):
        """ Test that the value is -1 when the metric source hasn't been configured. """
        self.assertEqual(-1, metric.RiskLog(project=domain.Project()).value())

    def test_comment_with_ignored_lists(self):
        """ Test that ignored lists are mentioned. """
        self.__board.ignored = ["Ignored list"]
        self.assertEqual("Genegeerde lijsten: Ignored list.", self.__metric.comment())

    def test_comment_without_ignored_lists(self):
        """ Test that the comment is empty when there are no ignored lists. """
        self.assertEqual("", self.__metric.comment())

    def test_multiple_comments(self):
        """ Test that comments are combined. """
        self.__board.ignored = ["Ignored list"]
        project = domain.Project(
            metric_sources={metric_source.RiskLog: self.__board},
            metric_source_ids={self.__board: 'board_id'},
            metric_options={metric.RiskLog: dict(comment="Comment.")})
        risk_log_metric = metric.RiskLog(project=project, subject=project)
        self.assertEqual("Comment. Genegeerde lijsten: Ignored list.", risk_log_metric.comment())


class UnreachableRiskLogTest(unittest.TestCase):
    """ Unit tests for the risk log metric when Trello is unreachable. """

    def setUp(self):
        board = UnreachableBoard()
        project = domain.Project(metric_sources={metric_source.RiskLog: board},
                                 metric_source_ids={board: 'board_id'})
        self.__metric = metric.RiskLog(project=project, subject=project)

    def test_url(self):
        """ Test that the url of the metric uses the url of the risk log board. """
        self.assertEqual({'Trello': 'http://trello.com'}, self.__metric.url())

    def test_value(self):
        """ Test that the value is -1. """
        self.assertEqual(-1, self.__metric.value())


@patch('hqlib.domain.Project')
class IssueLogMetricTest(unittest.TestCase):
    """ Unit tests for the action activity metric. """

    def test_convert_item_to_extra_info(self, project_mock):
        """ Test if arguments for extra info are comming in correct order. """
        project_mock.metric_sources.return_value = MagicMock()
        item = ("http://xx", "Description", "42")
        issue_log_metric = metric.IssueLogMetric(project=project_mock)
        expected_result = {"href": "http://xx", "text": "Description"}, "42"

        self.assertEqual(expected_result, issue_log_metric.convert_item_to_extra_info(item))


class ActionActivityTest(unittest.TestCase):
    """ Unit tests for the action activity metric. """

    def setUp(self):
        self.__board = FakeBoard()
        self.__project = domain.Project(metric_sources={metric_source.ActionLog: self.__board},
                                        metric_source_ids={self.__board: 'board_id'})
        self.__metric = metric.ActionActivity(project=self.__project, subject=self.__project)

    def test_value(self):
        """ Test that the board has been updated today. """
        self.assertEqual(0, self.__metric.value())

    def test_url(self):
        """ Test that url of the metric is equal to the url of the board. """
        self.assertEqual({FakeBoard.metric_source_name: self.__board.url()}, self.__metric.url())


class UnreachableActionActivityTest(unittest.TestCase):
    """ Unit tests for the action activity metric when Trello is unreachable. """

    def setUp(self):
        board = UnreachableBoard()
        project = domain.Project(metric_sources={metric_source.ActionLog: board},
                                 metric_source_ids={board: 'board_id'})
        self.__metric = metric.ActionActivity(project=project, subject=project)

    def test_value(self):
        """ Test that the value is -1. """
        self.assertEqual(-1, self.__metric.value())

    def test_url(self):
        """ Test that url of the metric is equal to the url of the board. """
        self.assertEqual({UnreachableBoard.metric_source_name: 'http://trello.com'}, self.__metric.url())


class OldActionsTest(unittest.TestCase):
    """ Unit tests for the old actions metric. """

    def setUp(self):
        board = FakeBoard()
        self.__project = domain.Project(metric_sources={metric_source.ActionLog: board},
                                        metric_source_ids={board: 'board_id'})
        self.__metric = metric.StaleActions(project=self.__project, subject=self.__project)

    def test_value(self):
        """ Test that the metric value equals the number of over due or inactive cards. """
        self.assertEqual(FakeBoard().nr_of_inactive_cards(), self.__metric.value())

    def test_url_label(self):
        """ Test that the metric has a url label. """
        self.assertTrue(self.__metric.url_label_text)


class UnreachableOldActionsTest(unittest.TestCase):
    """ Unit tests for the old actions metric when Trello is unreachable. """

    def setUp(self):
        board = UnreachableBoard()
        project = domain.Project(metric_sources={metric_source.ActionLog: board},
                                 metric_source_ids={board: 'board_id'})
        self.__metric = metric.StaleActions(project=project, subject=project)

    def test_value(self):
        """ Test that the value indicates a problem. """
        self.assertEqual(-1, self.__metric.value())

    def test_url(self):
        """ Test that url of the metric is equal to the url of the board. """
        self.assertEqual({UnreachableBoard.metric_source_name: 'http://trello.com'}, self.__metric.url())


class OverDueActionsTest(unittest.TestCase):
    """ Unit tests for the over due actions metric. """

    def setUp(self):
        board = FakeBoard()
        self.__project = domain.Project(metric_sources={metric_source.ActionLog: board},
                                        metric_source_ids={board: 'board_id'})
        self.__metric = metric.OverDueActions(project=self.__project, subject=self.__project)

    def test_value(self):
        """ Test that the metric value equals the number of over due or inactive cards. """
        self.assertEqual(5, self.__metric.value())

    def test_url(self):
        """ Test that url of the metric is equal to the url of the board. """
        self.assertEqual({'Trello': 'http://trello/board'}, self.__metric.url())

    def test_url_label(self):
        """ Test that the metric has a url label. """
        self.assertTrue(self.__metric.url_label_text)


class UnreachableOverDueActionsTest(unittest.TestCase):
    """ Unit tests for the over due actions metric when Trello is unreachable. """

    def setUp(self):
        board = UnreachableBoard()
        project = domain.Project(metric_sources={metric_source.ActionLog: board},
                                 metric_source_ids={board: 'board_id'})
        self.__metric = metric.OverDueActions(project=project, subject=project)

    def test_value(self):
        """ Test that the value indicates a problem. """
        self.assertEqual(-1, self.__metric.value())

    def test_url(self):
        """ Test that url of the metric is equal to the url of the board. """
        self.assertEqual({UnreachableBoard.metric_source_name: 'http://trello.com'}, self.__metric.url())
