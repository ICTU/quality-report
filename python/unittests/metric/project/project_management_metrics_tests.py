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

import datetime
import unittest

from qualitylib import metric, domain, metric_source
from qualitylib.metric_source import TrelloUnreachableException


class FakeBoard(object):
    """ Fake a Trello board. """
    @staticmethod
    def url():
        """ Return a fake url. """
        return 'http://trello/board'

    @staticmethod
    def date_of_last_update():
        """ Fake the date of the last update. """
        return datetime.datetime.now() - datetime.timedelta(minutes=1)

    @staticmethod
    def over_due_or_inactive_cards_url():
        """ Fake the url. """
        return 'http://trello/over_due_or_inactive_cards'

    @staticmethod
    def nr_of_over_due_or_inactive_cards():
        """ Fake the number. """
        return 5


class UnreachableBoard(object):
    """ Pretend that Trello is down. """
    @staticmethod
    def url():
        """ Fake that Trello is down. """
        raise TrelloUnreachableException

    @staticmethod
    def date_of_last_update():
        """ Fake that Trello is down. """
        raise TrelloUnreachableException

    @staticmethod
    def nr_of_over_due_or_inactive_cards():
        """ Fake that Trello is down. """
        raise TrelloUnreachableException

    @staticmethod
    def over_due_or_inactive_cards_url():
        """ Fake that Trello is down. """
        raise TrelloUnreachableException


class RiskLogTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the risk log metric. """

    def setUp(self):
        self.__project = domain.Project(
            metric_sources={metric_source.TrelloRiskBoard: FakeBoard()})
        self.__metric = metric.RiskLog(project=self.__project)

    def test_url(self):
        """ Test that the url of the metric uses the url of the risk log board. """
        self.assertEqual(dict(Trello=FakeBoard().url()), self.__metric.url())

    def test_value(self):
        """ Test that the value is the number of days since the last update. """
        self.assertEqual(0, self.__metric.value())

    def test_can_be_measured(self):
        """ Test that the risk log can be measured if there is a Trello board. """
        self.assertTrue(metric.RiskLog.can_be_measured(self.__project, self.__project))

    def test_cant_be_measured_without_risklog(self):
        """ Test that the risk log can't be measured if there is no Trello board. """
        project = domain.Project()
        self.assertFalse(metric.RiskLog.can_be_measured(project, project))


class UnreachableRiskLogTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the risk log metric when Trello is unreachable. """

    def setUp(self):
        project = domain.Project(metric_sources={metric_source.TrelloRiskBoard: UnreachableBoard()})
        self.__metric = metric.RiskLog(project=project)

    def test_url(self):
        """ Test that the url of the metric uses the url of the risk log board. """
        self.assertEqual(dict(Trello='http://trello.com'), self.__metric.url())

    def test_value(self):
        """ Test that the value is the number of days since the last update. """
        days = (datetime.datetime.now() - datetime.datetime(1, 1, 1)).days
        self.assertEqual(days, self.__metric.value())


class ActionActivityTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the action activity metric. """

    def setUp(self):  # pylint: disable=invalid-name
        self.__project = domain.Project(metric_sources={metric_source.TrelloActionsBoard: FakeBoard()})
        self.__metric = metric.ActionActivity(project=self.__project)

    def test_value(self):
        """ Test that the board has been updated today. """
        self.assertEqual(0, self.__metric.value())

    def test_url(self):
        """ Test that url of the metric is equal to the url of the board. """
        self.assertEqual(dict(Trello=FakeBoard().url()), self.__metric.url())

    def test_can_be_measured(self):
        """ Test that the metric can be measured when the project has an action list. """
        self.assertTrue(metric.ActionActivity.can_be_measured(self.__project, self.__project))

    def test_cant_be_measured(self):
        """ Test that the metric can not be measured when the project has no action list. """
        project = domain.Project()
        self.assertFalse(metric.ActionActivity.can_be_measured(project, project))


class UnreachableActionActivityTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the action activity metric when Trello is unreachable. """

    def setUp(self):
        project = domain.Project(metric_sources={metric_source.TrelloActionsBoard: UnreachableBoard()})
        self.__metric = metric.ActionActivity(project=project)

    def test_value(self):
        """ Test that the board has been updated today. """
        days = (datetime.datetime.now() - datetime.datetime(1, 1, 1)).days
        self.assertEqual(days, self.__metric.value())

    def test_url(self):
        """ Test that url of the metric is equal to the url of the board. """
        self.assertEqual(dict(Trello='http://trello.com'), self.__metric.url())


class ActionAgeTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the action age metric. """

    def setUp(self):
        self.__project = domain.Project(metric_sources={metric_source.TrelloActionsBoard: FakeBoard()})
        self.__metric = metric.ActionAge(project=self.__project)

    def test_value(self):
        """ Test that the metric value equals the number of over due or inactive cards. """
        self.assertEqual(FakeBoard().nr_of_over_due_or_inactive_cards(), self.__metric.value())

    def test_url(self):
        """ Test that url of the metric is equal to the url for the over due or inactive cards. """
        self.assertEqual(FakeBoard().over_due_or_inactive_cards_url(), self.__metric.url())

    def test_url_label(self):
        """ Test that the metric has a url label. """
        self.assertTrue(self.__metric.url_label())

    def test_can_be_measured(self):
        """ Test that the metric can be measured when the project has an action list. """
        self.assertTrue(metric.ActionAge.can_be_measured(self.__project, self.__project))

    def test_cant_be_measured(self):
        """ Test that the metric can not be measured when the project has no action list. """
        project = domain.Project()
        self.assertFalse(metric.ActionAge.can_be_measured(project, project))


class UnreachableActionAgeTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the action age metric when Trello is unreachable. """

    def setUp(self):
        project = domain.Project(metric_sources={metric_source.TrelloActionsBoard: UnreachableBoard()})
        self.__metric = metric.ActionAge(project=project)

    def test_value(self):
        """ Test that the value indicates a problem. """
        self.assertEqual(-1, self.__metric.value())

    def test_url(self):
        """ Test that url of the metric is equal to the url of the board. """
        self.assertEqual(dict(Trello='http://trello.com'), self.__metric.url())
