'''
Copyright 2012-2015 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import datetime
import unittest
from qualitylib import metric, utils, domain, metric_source
from qualitylib.metric_source import TrelloUnreachableException


class FakeBoard(object):
    ''' Fake a Trello board. '''
    @staticmethod
    def url():
        ''' Return a fake url. '''
        return 'http://trello/board'

    @staticmethod
    def date_of_last_update():
        ''' Fake the date of the last update. '''
        return datetime.datetime.now() - datetime.timedelta(minutes=1)

    @staticmethod
    def over_due_or_inactive_cards_url():
        ''' Fake the url. '''
        return 'http://trello/over_due_or_inactive_cards'

    @staticmethod
    def nr_of_over_due_or_inactive_cards():  # pylint: disable=invalid-name
        ''' Fake the number. '''
        return 5


class UnreachableBoard(object):
    ''' Pretend that Trello is down. '''
    @staticmethod
    def url():
        ''' Fake that Trello is down. '''
        raise TrelloUnreachableException

    @staticmethod
    def date_of_last_update():
        ''' Fake that Trello is down. '''
        raise TrelloUnreachableException

    @staticmethod
    def nr_of_over_due_or_inactive_cards():  # pylint: disable=invalid-name
        ''' Fake that Trello is down. '''
        raise TrelloUnreachableException

    @staticmethod
    def over_due_or_inactive_cards_url():
        ''' Fake that Trello is down. '''
        raise TrelloUnreachableException


class RiskLogTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the risk log metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__project = domain.Project(
            metric_sources={metric_source.TrelloRiskBoard: FakeBoard()})
        self.__metric = metric.RiskLog(project=self.__project)

    def test_url(self):
        ''' Test that the url of the metric uses the url of the risk log 
            board. '''
        self.assertEqual(dict(Trello=FakeBoard().url()), self.__metric.url())

    def test_value(self):
        ''' Test that the value is the number of days since the last 
            update. '''
        self.assertEqual(0, self.__metric.value())

    def test_can_be_measured(self):
        ''' Test that the risk log can be measured if there is a Trello 
            board. '''
        self.assertTrue(metric.RiskLog.can_be_measured(self.__project, 
                                                       self.__project))

    def test_cant_be_measured_without_risklog(self):
        ''' Test that the risk log can't be measured if there is no Trello 
            board. '''
        project = domain.Project()
        self.assertFalse(metric.RiskLog.can_be_measured(project, project))


class UnreachableRiskLogTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the risk log metric when Trello is unreachable. '''

    def setUp(self):  # pylint: disable=invalid-name
        project = domain.Project(
            metric_sources={metric_source.TrelloRiskBoard: UnreachableBoard()})
        self.__metric = metric.RiskLog(project=project)

    def test_url(self):
        ''' Test that the url of the metric uses the url of the risk log 
            board. '''
        self.assertEqual(dict(Trello='http://trello.com'), self.__metric.url())

    def test_value(self):
        ''' Test that the value is the number of days since the last 
            update. '''
        days = (datetime.datetime.now() - datetime.datetime(1, 1, 1)).days
        self.assertEqual(days, self.__metric.value())


class ActionActivityTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the action activity metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__project = domain.Project(
            metric_sources={metric_source.TrelloActionsBoard: FakeBoard()})
        self.__metric = metric.ActionActivity(project=self.__project)

    def test_value(self):
        ''' Test that the board has been updated today. '''
        self.assertEqual(0, self.__metric.value())

    def test_url(self):
        ''' Test that url of the metric is equal to the url of the board. '''
        self.assertEqual(dict(Trello=FakeBoard().url()), self.__metric.url())

    def test_can_be_measured(self):
        ''' Test that the metric can be measured when the project has a 
            action list. '''
        self.assertTrue(metric.ActionActivity.can_be_measured(self.__project, 
                                                              self.__project))

    def test_cant_be_measured(self):
        ''' Test that the metric can not be measured when the project has no 
            action list. '''
        project = domain.Project()
        self.assertFalse(metric.ActionActivity.can_be_measured(project, project))


class UnreachableActionActivityTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the action activity metric when Trello is 
        unreachable. '''

    def setUp(self):  # pylint: disable=invalid-name
        project = domain.Project(
            metric_sources={metric_source.TrelloActionsBoard: 
                            UnreachableBoard()})
        self.__metric = metric.ActionActivity(project=project)

    def test_value(self):
        ''' Test that the board has been updated today. '''
        days = (datetime.datetime.now() - datetime.datetime(1, 1, 1)).days
        self.assertEqual(days, self.__metric.value())

    def test_url(self):
        ''' Test that url of the metric is equal to the url of the board. '''
        self.assertEqual(dict(Trello='http://trello.com'), self.__metric.url())


class ActionAgeTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the action age metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__project = domain.Project(
            metric_sources={metric_source.TrelloActionsBoard: FakeBoard()})
        self.__metric = metric.ActionAge(project=self.__project)

    def test_value(self):
        ''' Test that the metric value equals the number of over due or 
            inactive cards. '''
        self.assertEqual(FakeBoard().nr_of_over_due_or_inactive_cards(), 
                         self.__metric.value())

    def test_url(self):
        ''' Test that url of the metric is equal to the url for the over due
            or inactive cards. '''
        self.assertEqual(FakeBoard().over_due_or_inactive_cards_url(), 
                         self.__metric.url())

    def test_url_label(self):
        ''' Test that the metric has a url label. '''
        self.assertTrue(self.__metric.url_label())

    def test_can_be_measured(self):
        ''' Test that the metric can be measured when the project has a 
            action list. '''
        self.assertTrue(metric.ActionAge.can_be_measured(self.__project, 
                                                         self.__project))

    def test_cant_be_measured(self):
        ''' Test that the metric can not be measured when the project has no 
            action list. '''
        project = domain.Project()
        self.assertFalse(metric.ActionAge.can_be_measured(project, project))


class UnreachableActionAgeTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the action age metric when Trello is unreachable. '''

    def setUp(self):  # pylint: disable=invalid-name
        project = domain.Project(
            metric_sources={metric_source.TrelloActionsBoard:
                            UnreachableBoard()})
        self.__metric = metric.ActionAge(project=project)

    def test_value(self):
        ''' Test that the value indicates a problem. '''
        self.assertEqual(-1, self.__metric.value())

    def test_url(self):
        ''' Test that url of the metric is equal to the url of the board. '''
        self.assertEqual(dict(Trello='http://trello.com'), self.__metric.url())


class FakeJira(object):
    ''' Fake Jira. '''
    def __init__(self, has_queries=True):
        self.__has_queries = has_queries

    def has_open_bugs_query(self):
        ''' Return whether Jira has an open bugs query. '''
        return self.__has_queries

    @staticmethod
    def nr_open_bugs():
        ''' Return a fake number of open bugs. '''
        return 7

    @staticmethod
    def nr_open_bugs_url():
        ''' Return a fake url for the nr of open bugs query. '''
        return 'http://openbugs/'

    def has_blocking_test_issues_query(self):
        ''' Return whether Jira has an blocking test issues query. '''
        return self.__has_queries

    @staticmethod
    def nr_blocking_test_issues():
        ''' Return a fake number of blocking test issues. '''
        return 5

    @staticmethod
    def nr_blocking_test_issues_url():
        ''' Return a fake url for the number of blocking test issues query. '''
        return 'http://blockingissues/'

    def has_open_security_bugs_query(self):
        ''' Return whether Jira has an open security bugs query. '''
        return self.__has_queries

    @staticmethod
    def nr_open_security_bugs():
        ''' Return a fake number of open security bugs. '''
        return 7

    @staticmethod
    def nr_open_security_bugs_url():
        ''' Return a fake url for the nr of open security bugs query. '''
        return 'http://opensecuritybugs/'


class OpenBugsTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the number of open bugs metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__project = domain.Project(metric_sources={metric_source.Jira: FakeJira()})
        self.__metric = metric.OpenBugs(project=self.__project)

    def test_value(self):
        ''' Test that the value is correct. '''
        self.assertEqual(FakeJira.nr_open_bugs(), self.__metric.value())

    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual({'Jira': FakeJira.nr_open_bugs_url()},
                         self.__metric.url())

    def test_can_be_measured(self):
        ''' Test that the metric can be measured when the project has Jira,
            and Jira has an open bugs query. '''
        self.assertTrue(metric.OpenBugs.can_be_measured(self.__project,
                                                        self.__project))

    def test_cant_be_measured_without_jira(self):
        ''' Test that the metric cannot be measured without Jira. '''
        project = domain.Project()
        self.assertFalse(metric.OpenBugs.can_be_measured(self.__project, project))

    def test_cant_be_measured_without_open_bugs_query(self):
        ''' Test that the metric cannot be measured without an open bugs query 
            in Jira. '''
        project = domain.Project(metric_sources={metric_source.Jira: 
                                                 FakeJira(has_queries=False)})
        self.assertFalse(metric.OpenBugs.can_be_measured(self.__project, project))


class OpenSecurityBugsTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the number of open security bugs metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__project = domain.Project(metric_sources={metric_source.Jira: 
                                                        FakeJira()})
        self.__metric = metric.OpenSecurityBugs(project=self.__project)

    def test_value(self):
        ''' Test that the value is correct. '''
        self.assertEqual(FakeJira.nr_open_security_bugs(),
                         self.__metric.value())

    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual({'Jira': FakeJira.nr_open_security_bugs_url()},
                         self.__metric.url())

    def test_can_be_measured(self):
        ''' Test that the metric can be measured when the project has Jira,
            and Jira has an open bugs query. '''
        self.assertTrue(metric.OpenSecurityBugs.can_be_measured(self.__project,
                                                                self.__project))

    def test_cant_be_measured_without_jira(self):
        ''' Test that the metric cannot be measured without Jira. '''
        project = domain.Project()
        self.assertFalse(metric.OpenSecurityBugs.can_be_measured(self.__project, 
                                                            project))

    def test_cant_be_measured_without_open_bugs_query(self):
        ''' Test that the metric cannot be measured without an open bugs query 
            in Jira. '''
        jira = FakeJira(has_queries=False)
        project = domain.Project(metric_sources={metric_source.Jira: jira})
        self.assertFalse(metric.OpenSecurityBugs.can_be_measured(self.__project,
                                                            project))


class BlockingTestIssuesTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the number of blocking test issues metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__project = domain.Project(metric_sources={metric_source.Jira:
                                                        FakeJira()})
        self.__metric = metric.BlockingTestIssues(project=self.__project)

    def test_value(self):
        ''' Test that the value is correct. '''
        self.assertEqual(FakeJira.nr_blocking_test_issues(),
                         self.__metric.value())

    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual({'Jira': FakeJira.nr_blocking_test_issues_url()},
                         self.__metric.url())

    def test_report(self):
        ''' Test that the report is correct. '''
        month = utils.format_month(utils.month_ago())
        self.assertEqual('Het aantal geopende blokkerende testbevindingen in '\
                         'de vorige maand (%s) was 5.' % month, 
                         self.__metric.report())

    def test_can_be_measured(self):
        ''' Test that the metric can be measured when the project has Jira,
            and Jira has an blocking test issues query. '''
        self.assertTrue(metric.BlockingTestIssues.can_be_measured( \
                        self.__project, self.__project))

    def test_cant_be_measured_without_jira(self):
        ''' Test that the metric cannot be measured without Jira. '''
        project = domain.Project()
        self.assertFalse(metric.BlockingTestIssues.can_be_measured(self.__project, 
                                                              project))

    def test_cant_be_measured_without_open_bugs_query(self):
        ''' Test that the metric cannot be measured without an open bugs query 
            in Jira. '''
        jira = FakeJira(has_queries=False)
        project = domain.Project(metric_sources={metric_source.Jira: jira})
        self.assertFalse(metric.BlockingTestIssues.can_be_measured(self.__project,
                                                              project))
