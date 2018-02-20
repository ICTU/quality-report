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

import unittest

from hqlib import metric, domain, metric_source


class FakeUnitTestReport(metric_source.UnitTestReport):
    """ Provide for a fake unittest report object so that the unit test don't need access to an actual report
        instance. """
    # pylint: disable=unused-argument

    def __init__(self, unittests=10):
        self.__unittests = unittests
        self.__failing_unittests = 5 if unittests else 0
        self.skipped = 0

    def passed_tests(self, *args):
        """ Return the number of unittests. """
        return self.__unittests - (self.__failing_unittests + self.skipped)

    def failed_tests(self, *args):
        """ Return the number of failing unittests. """
        return self.__failing_unittests

    def skipped_tests(self, *args):
        """ Return the number of skipped unittests. """
        return self.skipped


class FakeSubject(object):
    """ Provide for a fake subject. """
    @staticmethod
    def name():
        """ Return the name of the subject. """
        return 'FakeSubject'

    @staticmethod
    def metric_source_id(*args):  # pylint: disable=unused-argument
        """ Return the metric source id for the test report. """
        return 'http://report'


class FailingUnittestsTest(unittest.TestCase):
    """ Unit tests for the failing unit tests metric. """

    def setUp(self):  # pylint: disable=invalid-name
        """ Set up the fixture for the unit tests. """
        self.__report = FakeUnitTestReport()
        project = domain.Project(metric_sources={metric_source.UnitTestReport: self.__report})
        self.__metric = metric.FailingUnittests(subject=FakeSubject(), project=project)

    def test_value(self):
        """ Test that the value of the metric equals the value reported by the test report. """
        self.assertEqual(5, self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual('5 van de 10 unittesten falen.', self.__metric.report())

    def test_report_with_skipped_tests(self):
        """ Test that the report is correct when tests were skipped. """
        self.__report.skipped = 2
        self.assertEqual('5 van de 10 unittesten falen. 2 van de 10 unittesten zijn overgeslagen.',
                         self.__metric.report())

    def test_status_with_zero_unittests(self):
        """ Test that the metric is red when there are no unit tests. """
        report = FakeUnitTestReport(unittests=0)
        project = domain.Project(metric_sources={metric_source.UnitTestReport: report})
        failing_unittests = metric.FailingUnittests(subject=FakeSubject(), project=project)
        self.assertEqual('red', failing_unittests.status())

    def test_status_without_metric_source(self):
        """ Test that the metric is red when there is no metric source. """
        failing_unittests = metric.FailingUnittests(subject=FakeSubject(), project=domain.Project())
        self.assertEqual('red', failing_unittests.status())

    def test_report_with_zero_unittests(self):
        """ Test that the report is different when there are no unit tests. """
        report = FakeUnitTestReport(unittests=0)
        project = domain.Project(metric_sources={metric_source.UnitTestReport: report})
        failing_unittests = metric.FailingUnittests(subject=FakeSubject(), project=project)
        self.assertEqual('Er zijn geen unittesten.', failing_unittests.report())
