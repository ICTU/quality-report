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

from qualitylib import domain, metric_source
from unittests.domain.measurement.fake import FakeWiki, FakeHistory, FakeSubject
import datetime
import unittest


class MetricUnderTest(domain.Metric):
    # pylint: disable=too-few-public-methods
    """ Override Metric to implement abstract methods that are needed for running the unit tests. """
    def __init__(self, *args, **kwargs):
        self.date = None
        self.value_to_return = 0
        super(MetricUnderTest, self).__init__(*args, **kwargs)

    def value(self):
        """ Return the value of the metric. """
        return self.value_to_return

    def _date(self):
        if self.date:
            return self.date
        else:
            return super(MetricUnderTest, self)._date()  # pylint: disable=protected-access


class MetricTest(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """ Test case for the Metric domain class. """

    def setUp(self):  # pylint: disable=C0103
        self.__subject = FakeSubject()
        self.__project = domain.Project(
            metric_sources={metric_source.History: FakeHistory()})
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

    def test_default_status(self):
        """ Test that the default status is green. """
        self.assertEqual('green', self.__metric.status())

    def test_yellow_when_never_measured(self):
        """ Test that the status is yellow when the metric has never been measured. """
        self.__metric.old_age = datetime.timedelta(days=1)  # pylint: disable=attribute-defined-outside-init
        self.assertEqual('yellow', self.__metric.status())

    def test_yellow_when_old(self):
        """ Test that the status is yellow when the last measurement was too long ago. """
        self.__metric.old_age = datetime.timedelta(days=1)  # pylint: disable=attribute-defined-outside-init
        self.__metric.date = datetime.datetime.now() - datetime.timedelta(hours=25)
        self.assertEqual('yellow', self.__metric.status())

    def test_red_when_never_measured(self):
        """ Test that the status is red when the metric has never been measured. """
        self.__metric.max_old_age = datetime.timedelta(days=1)  # pylint: disable=attribute-defined-outside-init
        self.assertEqual('red', self.__metric.status())

    def test_red_when_old(self):
        """ Test that the status is red when the last measurement was too long ago. """
        self.__metric.max_old_age = datetime.timedelta(days=1)  # pylint: disable=attribute-defined-outside-init
        self.__metric.date = datetime.datetime.now() - datetime.timedelta(hours=25)
        self.assertEqual('red', self.__metric.status())

    def test_perfect_status(self):
        """ Test that the status is perfect when the value equals the perfect target. """
        self.__metric.perfect_value = 0  # pylint: disable=attribute-defined-outside-init
        self.assertEqual('perfect', self.__metric.status())

    def test_default_report(self):
        """ Test the default report. """
        self.assertEqual('Subclass responsibility', self.__metric.report())

    def test_report_with_long_subject(self):
        """ Test that the subject is abbreviated when long. """
        self.assertEqual('Subclass responsibility', self.__metric.report(max_subject_length=1))

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

    def test_comment_technical_debt(self):
        """ Test that the metric gets the comment from the subject when the subject has a reduced technical
            debt target. """
        # pylint: disable=attribute-defined-outside-init
        self.__subject.debt_target = domain.TechnicalDebtTarget(10, 'Comment')
        comment = self.__metric.comment()
        self.assertEqual('De op dit moment geaccepteerde technische schuld is 10. Comment', comment)

    def test_comment_technical_debt_url(self):
        """ Test that the metric has no comment url when the subject has a reduced technical debt target because
            the reduced technical debt target is specified in the project definition. """
        # pylint: disable=attribute-defined-outside-init
        self.__subject.debt_target = domain.TechnicalDebtTarget(10, 'Comment')
        urls = self.__metric.comment_urls()
        self.assertFalse(urls)

    def test_comment_from_wiki_url(self):
        """ Test that the comment urls include a link to the Wiki if the Wiki has a comment on the metric. """
        wiki = FakeWiki('Comment')
        project = domain.Project(
            metric_sources={metric_source.History: FakeHistory(), metric_source.Wiki: wiki})
        metric = MetricUnderTest(self.__subject, project=project)
        self.assertEqual(dict(Wiki=wiki.comment_url()), metric.comment_urls())

    def test_numerical_value(self):
        """ Test that the numerical value is the value by default. """
        self.assertEqual(self.__metric.numerical_value(), self.__metric.value())

    def test_status_start_date(self):
        """ Test that the metric gets the start date of the status from the history. """
        self.assertEqual(datetime.datetime(2013, 1, 1, 10, 0, 0), self.__metric.status_start_date())

    def test_product_version_type(self):
        """ Test that the product version type is no_product when the metric subject is not a product. """
        self.assertEqual('no_product', self.__metric.product_version_type())

    def test_metric_can_be_measured(self):
        """ Test that a metric can be measured if given a subject. """
        self.assertTrue(domain.Metric.can_be_measured(FakeSubject(), None))

    def test_metric_cant_be_measured(self):
        """ Test that a metric cannot be measured if not given a subject. """
        self.assertFalse(domain.Metric.can_be_measured(None, None))

    def test_metric_should_be_measured(self):
        """ Test that a metric should not be measured be default. """
        self.assertFalse(domain.Metric.should_be_measured(self.__project))

    def test_metric_missing(self):
        """ Test that the metric status is missing when the value is -1. """
        self.__metric.value_to_return = -1
        self.assertEqual('missing', self.__metric.status())


class LowerIsBetterMetricUnderTest(domain.LowerIsBetterMetric):
    # pylint: disable=too-few-public-methods
    """ Override LowerIsBetterMetric to implement abstract methods that are needed for running the unit tests. """
    def __init__(self, *args, **kwargs):
        self.__value = kwargs.pop('value', 0)
        super(LowerIsBetterMetricUnderTest, self).__init__(*args, **kwargs)

    def value(self):
        """ Return the measured value. """
        return self.__value


class LowerIsBetterMetricTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Test case for the LowerIsBetterMetric domain class. """

    def setUp(self):  # pylint: disable=C0103
        self.__subject = FakeSubject()
        self.__project = domain.Project(metric_sources={metric_source.History: FakeHistory()})

    def test_default_status(self):
        """ Test that the default status is perfect. """
        metric = LowerIsBetterMetricUnderTest(self.__subject, project=self.__project)
        self.assertEqual('perfect', metric.status())

    def test_impossible_value(self):
        """ Test that the status is missing if the value is below zero. """
        metric = LowerIsBetterMetricUnderTest(self.__subject, project=self.__project, value=-1)
        self.assertEqual('missing', metric.status())


class HigherIsBetterMetricUnderTest(domain.HigherIsBetterMetric):
    # pylint: disable=too-few-public-methods
    """ Override HigherIsBetterMetric to implement abstract methods that are needed for running the unit tests. """
    @staticmethod
    def value():
        """ Return the measured value. """
        return 0


class HigherIsBetterMetricTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Test case for the HigherIsBetterMetric domain class. """

    def setUp(self):  # pylint: disable=C0103
        self.__subject = FakeSubject()
        project = domain.Project(metric_sources={metric_source.History: FakeHistory()})
        self.__metric = HigherIsBetterMetricUnderTest(self.__subject, project=project)

    def test_default_status(self):
        """ Test that the default status is red. """
        self.assertEqual('red', self.__metric.status())

    def test_technical_debt(self):
        """ Test that the status is grey when the current value is accepted technical debt. """
        # pylint: disable=attribute-defined-outside-init
        self.__subject.technical_debt_target = lambda metric: domain.TechnicalDebtTarget(0, 'Comment')
        self.assertEqual('grey', self.__metric.status())


class LowerPercentageIsBetterMetricUnderTest(domain.LowerPercentageIsBetterMetric):
    # pylint: disable=too-few-public-methods
    """ Override LowerPercentageIsBetterMetric to implement abstract methods that are needed for running the
        unit tests. """
    low_target_value = 20
    target_value = 10
    numerator = 0
    denominator = 0

    def _numerator(self):
        return self.numerator

    def _denominator(self):
        return self.denominator


class PercentageMetricTestCase(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Test case for percentage metrics. """

    def setUp(self):  # pylint: disable=invalid-name
        self.__subject = FakeSubject()
        project = domain.Project(metric_sources={metric_source.History: FakeHistory()})
        self._metric = self.metric_under_test_class()(self.__subject, project=project)

    @staticmethod
    def metric_under_test_class():
        """ Return the metric class to be tested. """
        raise NotImplementedError  # pragma: no cover

    def set_metric_value(self, numerator, denominator):
        """ Set the metric value by means of the numerator and denominator. """
        # pylint: disable=attribute-defined-outside-init
        self._metric.numerator = numerator
        self._metric.denominator = denominator


class LowerPercentageIsBetterMetricTest(PercentageMetricTestCase):
    # pylint: disable=too-many-public-methods
    """ Test case for the LowerPercentageIsBetterMetric domain class. """

    @staticmethod
    def metric_under_test_class():
        return LowerPercentageIsBetterMetricUnderTest

    def test_perfect_status(self):
        """ Test that the default status is perfect when the score is 100%. """
        self.assertEqual('perfect', self._metric.status())

    def test_green_status(self):
        """ Test that the default status is green when the score is below the low target. """
        self.set_metric_value(1, 100)
        self.assertEqual('green', self._metric.status())

    def test_yellow_status(self):
        """ Test that the  status is yellow when the score is between the low target and target. """
        self.set_metric_value(20, 100)
        self.assertEqual('yellow', self._metric.status())

    def test_red_status(self):
        """ Test that the status is red when the score is higher than the low target. """
        self.set_metric_value(40, 100)
        self.assertEqual('red', self._metric.status())

    def test_y_axis_range(self):
        """ Test that the y axis range is 0-100. """
        self.assertEqual((0, 100), self._metric.y_axis_range())

    def test_default_report(self):
        """ Test that the default report. """
        self.set_metric_value(0, 0)
        self.assertEqual('Subclass responsibility', self._metric.report())


class HigherPercentageIsBetterMetricUnderTest(domain.HigherPercentageIsBetterMetric):
    # pylint: disable=too-few-public-methods
    """ Override HigherPercentageIsBetterMetric to implement abstract methods that are needed for running the
        unit tests. """
    low_target_value = 80
    target_value = 90
    numerator = 0
    denominator = 0

    def _numerator(self):
        return self.numerator

    def _denominator(self):
        return self.denominator


class HigherPercentageIsBetterMetricTest(PercentageMetricTestCase):
    # pylint: disable=too-many-public-methods
    """ Test case for the HigherPercentageIsBetterMetric domain class. """

    @staticmethod
    def metric_under_test_class():
        return HigherPercentageIsBetterMetricUnderTest

    def test_red_status(self):
        """ Test that the status is red when the percentage is lower than the low target. """
        self.set_metric_value(0, 5)
        self.assertEqual('red', self._metric.status())

    def test_yellow_status(self):
        """ Test that the status is yellow when the percentage is lower than the target. """
        self.set_metric_value(85, 100)
        self.assertEqual('yellow', self._metric.status())

    def test_green_status(self):
        """ Test that the status is green when the metric value is higher than the target value. """
        self.set_metric_value(95, 100)
        self.assertEqual('green', self._metric.status())

    def test_perfect_status(self):
        """ Test that the status is perfect when the metric value is 100%. """
        self.set_metric_value(100, 100)
        self.assertEqual('perfect', self._metric.status())

    def test_y_axis_range(self):
        """ Test that the y axis range is 0-100. """
        self.assertEqual((0, 100), self._metric.y_axis_range())

    def test_default_report(self):
        """ Test that the default report. """
        self.set_metric_value(0, 5)
        self.assertEqual('Subclass responsibility', self._metric.report())
