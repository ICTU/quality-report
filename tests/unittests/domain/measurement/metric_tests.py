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

from hqlib import domain, metric_source
from tests.unittests.domain.measurement.fake import FakeHistory, FakeSubject


class MetricUnderTest(domain.Metric):
    """ Override Metric to implement abstract methods that are needed for running the unit tests. """
    unit = 'foo'

    def __init__(self, *args, **kwargs):
        self.date = None
        self.value_to_return = 0
        super(MetricUnderTest, self).__init__(*args, **kwargs)

    def value(self):
        """ Return the value of the metric. """
        return self.value_to_return

    def _date(self):
        return self.date if self.date else super(MetricUnderTest, self)._date()

    def _is_value_better_than(self, target):
        """ Return a dummy value. """
        return True


class MetricTest(unittest.TestCase):
    """ Test case for the Metric domain class. """

    def setUp(self):
        self.__subject = FakeSubject()
        self.__project = domain.Project(metric_sources={metric_source.History: FakeHistory()})
        self.__metric = MetricUnderTest(self.__subject, project=self.__project)

    def test_stable_id(self):
        """ Test that the metric has a stable id. """
        self.assertEqual('MetricUnderTestFakeSubject', self.__metric.stable_id())

    def test_stable_id_mutable_subject(self):
        """ Test that the stable id doesn't include the subject if the subject is a list. """
        self.assertEqual('Metric', domain.Metric([], project=domain.Project()).stable_id())

    def test_set_id_string(self):
        """ Test that the id string can be changed. """
        self.__metric.set_id_string('id string')
        self.assertEqual('id string', self.__metric.id_string())

    def test_one_metric_source(self):
        """ Test that the correct metric source id is returned when there is one metric source instance. """
        MetricUnderTest.metric_source_classes = [metric_source.Birt]
        project = domain.Project(metric_sources={metric_source.Birt: 'Birt1'})
        product = domain.Product(project, metric_source_ids={'Birt1': 'birt id'})
        # pylint: disable=protected-access
        self.assertEqual('birt id', MetricUnderTest(project=project, subject=product)._metric_source_id)
        MetricUnderTest.metric_source_classes = []

    def test_multiple_metric_sources(self):
        """ Test that the correct metric source id is returned when there are multiple metric source instances. """
        MetricUnderTest.metric_source_classes = [metric_source.Birt]
        project = domain.Project(metric_sources={metric_source.Birt: ['Birt1', 'Birt2']})
        product = domain.Product(project, metric_source_ids={'Birt2': 'birt id'})
        # pylint: disable=protected-access
        self.assertEqual('birt id', MetricUnderTest(project=project, subject=product)._metric_source_id)
        MetricUnderTest.metric_source_classes = []

    def test_no_matching_metric_source(self):
        """ Test that no metric source id is returned when there is no metric source instance for the product. """
        MetricUnderTest.metric_source_classes = [metric_source.Birt]
        project = domain.Project(metric_sources={metric_source.Birt: ['Birt1']})
        product = domain.Product(project, metric_source_ids={'Birt2': 'birt id'})
        # pylint: disable=protected-access
        self.assertFalse(MetricUnderTest(project=project, subject=product)._metric_source_id)
        MetricUnderTest.metric_source_classes = []

    def test_default_report(self):
        """ Test the default report. """
        self.assertEqual('Subclass responsibility', self.__metric.report())

    def test_report_with_long_subject(self):
        """ Test that the subject is abbreviated when long. """
        self.assertEqual('Subclass responsibility', self.__metric.report(max_subject_length=1))

    def test_missing_metric_source_report(self):
        """ Test that the metric report explains which metric source needs to be configured. """
        # pylint: disable=attribute-defined-outside-init
        self.__metric.metric_source_classes = [metric_source.VersionControlSystem]
        self.assertEqual('De subclass responsibility van FakeSubject kon niet gemeten worden omdat niet alle '
                         'benodigde bronnen zijn geconfigureerd. Configureer de volgende bron(nen): '
                         'VersionControlSystem.', self.__metric.report())

    def test_missing_metric_source_id_report(self):
        """ Test that the metric report explains which metric source ids need to be configured. """
        project = domain.Project(metric_sources={metric_source.TestReport: metric_source.JunitTestReport()})
        metric = MetricUnderTest(self.__subject, project=project)
        metric.metric_source_classes = [metric_source.TestReport]
        self.assertEqual('De subclass responsibility van FakeSubject kon niet gemeten worden omdat niet alle '
                         'benodigde bron-ids zijn geconfigureerd. Configureer ids voor de volgende bronnen: '
                         'TestReport.', metric.report())

    def test_missing_metric_report(self):
        """ Test that the metric report is adapted when the value is missing. """
        self.__metric.value_to_return = -1
        self.assertEqual('De subclass responsibility van FakeSubject kon niet gemeten worden omdat niet alle '
                         'benodigde bronnen beschikbaar zijn.', self.__metric.report())

    def test_default_norm(self):
        """ Test the default norm. """
        self.assertEqual('Subclass responsibility', self.__metric.norm())

    def test_missing_norm_parameter(self):
        """ Test that the norm method raises an exception when not all parameters for the norm description
            are supplied. """
        self.__metric.norm_template += '{missing_parameter}'  # pylint: disable=no-member
        self.assertRaises(KeyError, self.__metric.norm)

    def test_default_url(self):
        """ Test that the metric has no default url. """
        self.assertFalse(self.__metric.url())

    def test_default_url_label(self):
        """ Test that the metric has no default url label. """
        self.assertFalse(self.__metric.url_label())

    def test_recent_history(self):
        """ Test that the metric has no history by default. """
        self.assertFalse(self.__metric.recent_history())

    def test_default_y_axis_range(self):
        """ Test that the default y axis range is 0-100. """
        self.assertEqual((0, 100), self.__metric.y_axis_range())

    def test_y_axis_range(self):
        """ Test that the y axis range depends on the history. """
        FakeHistory.values = [1, 4, 5, 2]
        self.assertEqual((1, 5), self.__metric.y_axis_range())

    def test_y_axis_range_zero(self):
        """ Test that the y axis range is -1, 1 when the minimum and maximum historic values are zero. """
        FakeHistory.values = [0]
        self.assertEqual((-1, 1), self.__metric.y_axis_range())

    def test_default_target(self):
        """ Test that the default target is a subclass responsibility. """
        self.assertEqual('Subclass responsibility', self.__metric.target())

    def test_subject_target(self):
        """ Test that the metric gets the target value from the subject if it has one. """
        # pylint: disable=attribute-defined-outside-init
        self.__subject.target = lambda subject: 'Subject specific target'
        self.assertEqual('Subject specific target', self.__metric.target())

    def test_default_low_target(self):
        """ Test that the default low target is a subclass responsibility. """
        self.assertEqual('Subclass responsibility', self.__metric.low_target())

    def test_subject_low_target(self):
        """ Test that the metric gets the low target value from the subject if it has one. """
        # pylint: disable=attribute-defined-outside-init
        self.__subject.low_target = lambda metric: 'Subject specific target'
        self.assertEqual('Subject specific target', self.__metric.low_target())

    def test_default_comment(self):
        """ Test that the metric has no comment by default. """
        self.assertEqual('', self.__metric.comment())

    def test_default_comment_urls(self):
        """ Test that the metric has no comment urls by default. """
        self.assertEqual({}, self.__metric.comment_urls())

    def test_default_comment_url_label(self):
        """ Test that the metric has no comment url label by default. """
        self.assertFalse(self.__metric.comment_url_label())

    def test_subject_comment(self):
        """ Test that the metric uses the comment from the subject. """
        self.__subject.options['comment'] = 'Comment'
        self.assertEqual('Comment', self.__metric.comment())

    def test_subject_comment_url(self):
        """ Test that the metric has no comment url when the subject has a comment because the comment is specified
            in the project definition. """
        self.__subject.options['comment'] = 'Comment'
        self.assertFalse(self.__metric.comment_urls())

    def test_comment_technical_debt(self):
        """ Test that the metric gets the comment from the subject when the subject has a reduced technical
            debt target. """
        self.__subject.debt_target = domain.TechnicalDebtTarget(10, 'Comment')
        self.assertEqual('De op dit moment geaccepteerde technische schuld is 10 foo. Comment', self.__metric.comment())

    def test_comment_technical_debt_url(self):
        """ Test that the metric has no comment url when the subject has a reduced technical debt target because
            the reduced technical debt target is specified in the project definition. """
        self.__subject.debt_target = domain.TechnicalDebtTarget(10, 'Comment')
        self.assertFalse(self.__metric.comment_urls())

    def test_subject_and_debt_comment(self):
        """ Test that the subject's comment and the technical debt comment are combined. """
        self.__subject.options['comment'] = 'Subject.'
        self.__subject.debt_target = domain.TechnicalDebtTarget(10, 'Debt.')
        self.assertEqual('De op dit moment geaccepteerde technische schuld is 10 foo. Debt. Subject.',
                         self.__metric.comment())

    def test_numerical_value(self):
        """ Test that the numerical value is the value by default. """
        self.assertEqual(self.__metric.numerical_value(), self.__metric.value())

    def test_status_start_date(self):
        """ Test that the metric gets the start date of the status from the history. """
        self.assertEqual(datetime.datetime(2013, 1, 1, 10, 0, 0), self.__metric.status_start_date())

    def test_metric_should_be_measured(self):
        """ Test that a metric should not be measured be default. """
        self.assertFalse(domain.Metric.should_be_measured(self.__project))


class MetricStatusTest(unittest.TestCase):
    """ Test case for the Metric domain class status method. """

    def setUp(self):
        self.__subject = FakeSubject()
        self.__metric = MetricUnderTest(self.__subject, project=domain.Project())

    def assert_status(self, expected_status):
        """ Assert that the metric has the expected status. """
        self.assertEqual(expected_status, self.__metric.status())

    def test_default_status(self):
        """ Test that the default status is green. """
        self.assertEqual('green', self.__metric.status())

    def test_missing_metric_sources_status(self):
        """ Test that the status is missing metric sources when the project doesn't have the required metric source. """
        # pylint: disable=attribute-defined-outside-init
        self.__metric.metric_source_classes = [metric_source.VersionControlSystem]
        self.assert_status('missing_source')

    def test_missing_metric_source_id_status(self):
        """ Test that the status is missing metric sources when the subject doesn't have the required metric source
            id. """
        project = domain.Project(metric_sources={metric_source.TestReport: metric_source.JunitTestReport()})
        metric = MetricUnderTest(self.__subject, project=project)
        metric.metric_source_classes = [metric_source.TestReport]
        self.assertEqual('missing_source', metric.status())

    def test_missing_metric(self):
        """ Test that the metric status is missing when the value is -1. """
        self.__metric.value_to_return = -1
        self.assert_status('missing')

    def test_yellow_when_never_measured(self):
        """ Test that the status is yellow when the metric has never been measured. """
        self.__metric.old_age = datetime.timedelta(days=1)  # pylint: disable=attribute-defined-outside-init
        self.assert_status('yellow')

    def test_yellow_when_old(self):
        """ Test that the status is yellow when the last measurement was too long ago. """
        self.__metric.old_age = datetime.timedelta(days=1)  # pylint: disable=attribute-defined-outside-init
        self.__metric.date = datetime.datetime.now() - datetime.timedelta(hours=25)
        self.assert_status('yellow')

    def test_red_when_never_measured(self):
        """ Test that the status is red when the metric has never been measured. """
        self.__metric.max_old_age = datetime.timedelta(days=1)  # pylint: disable=attribute-defined-outside-init
        self.assert_status('red')

    def test_red_when_old(self):
        """ Test that the status is red when the last measurement was too long ago. """
        self.__metric.max_old_age = datetime.timedelta(days=1)  # pylint: disable=attribute-defined-outside-init
        self.__metric.date = datetime.datetime.now() - datetime.timedelta(hours=25)
        self.assert_status('red')

    def test_perfect_status(self):
        """ Test that the status is perfect when the value equals the perfect target. """
        self.__metric.perfect_value = 0  # pylint: disable=attribute-defined-outside-init
        self.assert_status('perfect')

    def test_status_when_technical_debt(self):
        """ Test that the status is grey when the metric has accepted technical debt. """
        self.__metric.old_age = datetime.timedelta(days=1)  # pylint: disable=attribute-defined-outside-init
        self.__subject.debt_target = domain.TechnicalDebtTarget(10, 'Debt.')
        self.assert_status('grey')
