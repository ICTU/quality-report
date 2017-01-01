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

import datetime
import unittest

from hqlib import metric, domain, metric_source


class FakeNCover(domain.MetricSource):
    """ Fake NCover. """
    metric_source_name = metric_source.NCover.metric_source_name
    needs_metric_source_id = metric_source.CoverageReport.needs_metric_source_id
    url = 'http://ncover'

    @staticmethod
    def statement_coverage(ncover_id):  # pylint: disable=unused-argument
        """ Return the ART coverage. """
        return 98

    branch_coverage = statement_coverage

    @staticmethod
    def coverage_date(ncover_id):  # pylint: disable=unused-argument
        """ Return a fake date. """
        return datetime.datetime.today() - datetime.timedelta(days=4)


class FakeJaCoCo(FakeNCover):
    """ Fake JaCoCo. """
    metric_source_name = metric_source.JaCoCo.metric_source_name
    url = 'http://jacoco'


class FakeSubject(object):
    """ Provide for a fake subject. """
    def __init__(self, art='', metric_source_ids=None):
        self.__art = art
        self.__metric_source_ids = metric_source_ids or dict()

    @staticmethod
    def name():
        """ Return the name of the subject. """
        return 'FakeSubject'

    def metric_source_id(self, the_metric_source):
        """ Return the id of the subject for the metric source. """
        return self.__metric_source_ids.get(the_metric_source)


class ARTStatementCoverageJacocoTest(unittest.TestCase):
    """ Unit tests for the ART coverage metric. """
    metric_class = metric.ARTStatementCoverage
    metric_source_class = FakeJaCoCo
    metric_source_id = 'http://jacoco'

    def setUp(self):
        self.__coverage_report = self.metric_source_class()
        self.__subject = FakeSubject(metric_source_ids={self.__coverage_report: self.metric_source_id})
        self.__project = domain.Project(metric_sources={metric_source.CoverageReport: self.__coverage_report})
        self.__metric = self.metric_class(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that value of the metric equals the coverage as reported by Jacoco. """
        self.assertEqual(self.__coverage_report.statement_coverage(None), self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({self.metric_source_class.metric_source_name: self.metric_source_id}, self.__metric.url())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertTrue(self.__metric.report().startswith(
            'FakeSubject ART {} coverage is 98%'.format(self.metric_class.covered_item)))

    def test_missing_id(self):
        """ Test that the value is -1 when the metric source id hasn't been configured. """
        subject = FakeSubject()
        coverage_metric = self.metric_class(subject=subject, project=self.__project)
        self.assertEqual(-1, coverage_metric.value())

    def test_old_age(self):
        """ Test that the old age is set for trunk versions. """
        self.assertEqual(datetime.timedelta(hours=3 * 24), self.__metric.old_age)


class ARTBranchCoverageJacocoTest(ARTStatementCoverageJacocoTest):
    """ Unit tests for the ART branch metric. """
    metric_class = metric.ARTBranchCoverage


class ARTStatementCoverageNCoverTest(ARTStatementCoverageJacocoTest):
    """ Unit tests for the ART statement coverage metric. """
    metric_class = metric.ARTStatementCoverage
    metric_source_class = FakeNCover
    metric_source_id = 'http://ncover'


class ARTBranchCoverageNCoverTest(ARTStatementCoverageNCoverTest):
    """ Unit tests for the ART branch coverage metric. """
    metric_class = metric.ARTBranchCoverage


class FakeJenkinsTestReport(domain.MetricSource):
    """ Fake a Jenkins test report instance for unit test purposes. """
    metric_source_name = metric_source.JenkinsTestReport.metric_source_name
    needs_metric_source_id = True

    def __init__(self):
        self.passed = 14
        super(FakeJenkinsTestReport, self).__init__()

    @staticmethod
    def failed_tests(*args):  # pylint: disable=unused-argument
        """ Return the number of failing tests for the job. """
        return 4

    @staticmethod
    def skipped_tests(*args):  # pylint: disable=unused-argument
        """ Return the number of skipped tests for the job. """
        return 2

    def passed_tests(self, *args):  # pylint: disable=unused-argument
        """ Return the number of passed tests for the job. """
        return self.passed

    def report_datetime(self, *args):  # pylint: disable=unused-argument
        """ Return the number of passed tests for the job. """
        return datetime.datetime.min if self.passed < 0 else datetime.datetime(2016, 1, 1, 12, 0, 0)


class FailingRegressionTestsTest(unittest.TestCase):
    """ Unit tests for the failing regression tests metric. """
    def setUp(self):
        self.__jenkins = FakeJenkinsTestReport()
        self.__subject = FakeSubject(metric_source_ids={self.__jenkins: 'jenkins_job'})
        self.__project = domain.Project(metric_sources={metric_source.TestReport: self.__jenkins})
        self.__metric = metric.FailingRegressionTests(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that value of the metric equals the failing tests as reported by Jenkins. """
        self.assertEqual(self.__jenkins.failed_tests('jenkins_job') + self.__jenkins.skipped_tests('jenkins_job'),
                         self.__metric.value())

    def test_value_multiple_jobs(self):
        """ Test that the value of the metric equals to total number of failing tests if there are multiple
            test reports. """
        subject = FakeSubject(metric_source_ids={self.__jenkins: ['a', 'b']})
        failing_tests = metric.FailingRegressionTests(subject=subject, project=self.__project)
        expected = self.__jenkins.failed_tests('a', 'b') + self.__jenkins.skipped_tests('a', 'b')
        self.assertEqual(expected, failing_tests.value())

    def test_value_when_missing(self):
        """ Test that the value is negative when the test report is missing. """
        self.__jenkins.passed = -1
        self.assertTrue(self.__metric.value() < 0)

    def test_report(self):
        """ Test that the report for the metric is correct. """
        self.assertEqual('6 van de 20 regressietesten van FakeSubject slagen niet.', self.__metric.report())

    def test_url(self):
        """ Test that the url points to the Jenkins job. """
        self.assertEqual({'Jenkins testreport': 'jenkins_job'}, self.__metric.url())

    def test_url_multiple_jobs(self):
        """ Test that the url points to the Jenkins jobs. """
        subject = FakeSubject(metric_source_ids={self.__jenkins: ['a', 'b']})
        failing_tests = metric.FailingRegressionTests(subject=subject, project=self.__project)
        self.assertEqual({'Jenkins testreport (1/2)': 'a', 'Jenkins testreport (2/2)': 'b'}, failing_tests.url())


class RegressionTestAgeTest(unittest.TestCase):
    """ Unit tests for the regression test age metric. """
    def setUp(self):
        self.__jenkins = FakeJenkinsTestReport()
        self.__subject = FakeSubject(metric_source_ids={self.__jenkins: 'jenkins_job'})
        self.__project = domain.Project(metric_sources={metric_source.TestReport: self.__jenkins})
        self.__metric = metric.RegressionTestAge(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that value of the metric equals the report date as reported by Jenkins. """
        expected = (datetime.datetime.now() - self.__jenkins.report_datetime('jenkins_job')).days
        self.assertEqual(expected, self.__metric.value())

    def test_value_multiple_jobs(self):
        """ Test that the value of the metric equals to minimum report age if there are multiple
            test reports. """
        subject = FakeSubject(metric_source_ids={self.__jenkins: ['a', 'b']})
        age = metric.RegressionTestAge(subject=subject, project=self.__project)
        expected = (datetime.datetime.now() - self.__jenkins.report_datetime('a', 'b')).days
        self.assertEqual(expected, age.value())

    def test_value_when_missing(self):
        """ Test that the value is negative when the test report is missing. """
        self.__jenkins.passed = -1
        self.assertTrue(self.__metric.value() < 0)

    def test_report(self):
        """ Test that the report for the metric is correct. """
        days = (datetime.datetime.now() - self.__jenkins.report_datetime()).days
        self.assertEqual('De regressietest van FakeSubject is {} dagen geleden gedraaid.'.format(days),
                         self.__metric.report())

    def test_url(self):
        """ Test that the url points to the Jenkins job. """
        self.assertEqual({'Jenkins testreport': 'jenkins_job'}, self.__metric.url())

    def test_url_multiple_jobs(self):
        """ Test that the url points to the Jenkins jobs. """
        subject = FakeSubject(metric_source_ids={self.__jenkins: ['a', 'b']})
        failing_tests = metric.RegressionTestAge(subject=subject, project=self.__project)
        self.assertEqual({'Jenkins testreport (1/2)': 'a', 'Jenkins testreport (2/2)': 'b'}, failing_tests.url())
