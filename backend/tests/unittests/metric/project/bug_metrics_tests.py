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

from hqlib import metric, domain, metric_source, requirement


class FakeJira(object):
    """ Fake Jira. """

    metric_source_name = metric_source.Jira.metric_source_name
    needs_metric_source_id = metric_source.Jira.needs_metric_source_id

    @staticmethod
    def nr_open_bugs():
        """ Return a fake number of open bugs. """
        return 7

    @staticmethod
    def nr_open_bugs_url():
        """ Return a fake url for the nr of open bugs query. """
        return 'http://openbugs/'

    @staticmethod
    def nr_open_security_bugs():
        """ Return a fake number of open security bugs. """
        return 7

    @staticmethod
    def nr_open_security_bugs_url():
        """ Return a fake url for the nr of open security bugs query. """
        return 'http://opensecuritybugs/'

    @staticmethod
    def nr_open_static_security_analysis_bugs():
        """ Return a fake number of static security analysis bugs. """
        return 8

    @staticmethod
    def nr_open_static_security_analysis_bugs_url():
        """ Return a fake url for the number of open static security analysis bugs query. """
        return 'http://openstaticsecurityanalysisbugs/'

    @staticmethod
    def nr_technical_debt_issues():
        """ Return the number of technical debt issues. """
        return 8

    @staticmethod
    def nr_technical_debt_issues_url():
        """ Return a fake url for the number of technical debt issues query. """
        return 'http://technicaldebtissues/'


class OpenBugsTest(unittest.TestCase):
    """ Unit tests for the number of open bugs metric. """

    def setUp(self):
        self.__project = domain.Project(metric_sources={metric_source.Jira: FakeJira()},
                                        requirements=[requirement.TrackBugs])
        self.__metric = metric.OpenBugs(project=self.__project)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(FakeJira.nr_open_bugs(), self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({'Jira': FakeJira.nr_open_bugs_url()}, self.__metric.url())


class OpenSecurityBugsTest(unittest.TestCase):
    """ Unit tests for the number of open security bugs metric. """

    def setUp(self):
        self.__project = domain.Project(metric_sources={metric_source.Jira: FakeJira()},
                                        requirements=[requirement.TrackBugs])
        self.__metric = metric.OpenSecurityBugs(project=self.__project)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(FakeJira.nr_open_security_bugs(), self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({'Jira': FakeJira.nr_open_security_bugs_url()}, self.__metric.url())


class OpenStaticSecurityAnalysisBugsTest(unittest.TestCase):
    """ Unit tests for the number of open static security analysis bugs metric. """

    def setUp(self):
        self.__project = domain.Project(metric_sources={metric_source.Jira: FakeJira()},
                                        requirements=[requirement.TrackBugs])
        self.__metric = metric.OpenStaticSecurityAnalysisBugs(project=self.__project)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(FakeJira.nr_open_static_security_analysis_bugs(), self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({'Jira': FakeJira.nr_open_static_security_analysis_bugs_url()}, self.__metric.url())


class TechnicalDebtIssuesTest(unittest.TestCase):
    """ Unit tests for the number of technical debt issues metric. """

    def setUp(self):
        self.__project = domain.Project(metric_sources={metric_source.Jira: FakeJira()},
                                        requirements=[requirement.TrackTechnicalDebt])
        self.__metric = metric.TechnicalDebtIssues(project=self.__project)

    def test_value(self):
        """ Test that the value is correct. """
        self.assertEqual(FakeJira.nr_technical_debt_issues(), self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({'Jira': FakeJira.nr_technical_debt_issues_url()}, self.__metric.url())
