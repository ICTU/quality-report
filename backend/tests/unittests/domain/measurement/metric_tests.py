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

import json
import datetime
import unittest

from unittest.mock import MagicMock, patch
from hqlib import domain, metric_source
from tests.unittests.domain.measurement.fake import FakeHistory, FakeSubject


class MetricUnderTest(domain.Metric):
    """ Override Metric to implement abstract methods that are needed for running the unit tests. """
    unit = 'foo'

    def __init__(self, *args, **kwargs):
        self.value_to_return = 0
        super().__init__(*args, **kwargs)

    def value(self):
        """ Return the value of the metric. """
        return self.value_to_return

    def _is_value_better_than(self, target):  # pylint: disable=unused-argument
        """ Return a dummy value. """
        return True  # pragma: no cover


class MetricTest(unittest.TestCase):
    """ Test case for the Metric domain class. """

    def setUp(self):
        self.__subject = FakeSubject()
        self.__project = domain.Project(metric_sources={metric_source.History: FakeHistory()})
        self.__metric = MetricUnderTest(self.__subject, project=self.__project)

    def test_stable_id(self):
        """ Test that the metric has a stable id. """
        self.assertEqual('MetricUnderTestFakeSubject', self.__metric.stable_id())

    def test_normalized_stable_id(self):
        """ Test that it returns stable id with _ instead of non-alphanumeric characters . """

        result = self.__metric.normalized_stable_id()

        self.assertEqual('MetricUnderTestFakeSubject_', result)

    @patch.object(MetricUnderTest, 'stable_id')
    def test_normalized_stable_id_with_non_alphanumerics(self, mock_stable_id):
        """ Test that it returns stable id with _ instead of non-alphanumeric characters . """
        mock_stable_id.return_value = 'q3@a "a>_-\\/'

        result = self.__metric.normalized_stable_id()

        self.assertEqual('q3_a__a_____', result[:result.rfind('_')])
        self.assertEqual('6432346295459247', result[result.rfind('_') + 1:])

    def test_stable_id_mutable_subject(self):
        """ Test that the stable id doesn't include the subject if the subject is a list. """
        self.assertEqual('Metric', domain.Metric([], project=domain.Project()).stable_id())

    def test_format_text_without_links(self):
        """ Test that the formatted text is not followed by anything. """
        self.assertEqual("Some text...", self.__metric.format_text_with_links('Some text...'))

    def test_format_comment_with_links(self):
        """ Test that the formatted text is followed by a comma separated list of keys. """
        self.assertEqual("Some text... [{'href': 'http://url/br1', 'text': 'branch_1'}, "
                         "{'href': 'http://url/br2', 'text': 'branch_2'}]",
                         self.__metric.format_comment_with_links(
                             'Some text...', {"branch_1": "http://url/br1", "branch_2": "http://url/br2"}, ""))

    def test_format_comment_quotes(self):
        """ Test that the quotes in formatted text are correctly escaped. """
        self.assertEqual("Someone's \\\"text\\\"...",
                         self.__metric.format_comment_with_links('Someone\'s "text"...', {}, ""))

    def test_format_comment_with_links_in_text(self):
        """ Test that the link in the text is changed to href. """
        self.assertEqual("Some {'href': 'http://a.href/sub/x/s/', 'text': 'http://a.href/sub/x/s/'} text...",
                         self.__metric.format_comment_with_links('Some http://a.href/sub/x/s/ text...', {}, 'ignored'))

    def test_format_comment_with_links_with_port_in_text(self):
        """ Test that the link with a port number in the text is changed to href. """
        self.assertEqual("Some {'href': 'http://a.href:8080/sub/', 'text': 'http://a.href:8080/sub/'} text...",
                         self.__metric.format_comment_with_links('Some http://a.href:8080/sub/ text...', {}, 'ignored'))

    def test_format_comment_with_links_with_www_in_text(self):
        """ Test that the link containing www in the text is changed to href. """
        self.assertEqual("Some {'href': 'http://www.href/sub', 'text': 'http://www.href/sub'} text...",
                         self.__metric.format_comment_with_links('Some http://www.href/sub text...', {}, 'ignored'))

    def test_format_comment_with_links_with_www_in_text_xx(self):
        """ Test that the url without http is treated as a text. """
        self.assertEqual("Some www.href/sub text...",
                         self.__metric.format_comment_with_links('Some www.href/sub text...', {}, 'ignored'))

    def test_format_comment_with_links_with_params_in_text(self):
        """ Test that the link containing url parameter in the text is changed to href. """
        self.assertEqual("Some {'href': 'http://a.href?param=1', 'text': 'http://a.href?param=1'} text...",
                         self.__metric.format_comment_with_links('Some http://a.href?param=1 text...', {}, 'ignored'))

    def test_format_comment_with_links_with_label(self):
        """ Test that the formatted text is followed by a comma separated list of keys. """
        self.assertEqual("Some text... [Label: {'href': 'http://url/br1', 'text': 'branch_1'}, "
                         "{'href': 'http://url/br2', 'text': 'branch_2'}]",
                         self.__metric.format_comment_with_links(
                             'Some text...', {"branch_1": "http://url/br1", "branch_2": "http://url/br2"}, "Label"))

    @patch.object(domain.Metric, '_metric_source_urls')
    def test_format_text_with_links(self, mock_metric_source_urls):
        """ Test that comment formatting function is the same as the text formatting one."""
        mock_metric_source_urls.return_value = ['http://url1']
        mock_metric_source = MagicMock()
        mock_metric_source.metric_source_name = "Text"
        project = MagicMock()
        project.metric_sources.return_value = [mock_metric_source]
        test_metric = domain.Metric(subject=MagicMock(), project=project)

        self.assertEqual("Some text... [{'href': 'http://url1', 'text': 'Text'}]",
                         test_metric.format_text_with_links('Some text...'))

    @patch.object(domain.Metric, '_metric_source_urls')
    def test_format_text_with_links_unknown_source(self, mock_metric_source_urls):
        """ Test that comment formatting function is the same as the text formatting one."""
        mock_metric_source_urls.return_value = ['http://url1']
        project = MagicMock()
        project.metric_sources.return_value = []
        test_metric = domain.Metric(subject=MagicMock(), project=project)

        self.assertEqual("Some text... [{'href': 'http://url1', 'text': 'Unknown metric source'}]",
                         test_metric.format_text_with_links('Some text...'))

    def test_set_id_string(self):
        """ Test that the id string can be changed. """
        self.__metric.set_id_string('id string')
        self.assertEqual('id string', self.__metric.id_string())

    def test_one_metric_source(self):
        """ Test that the correct metric source id is returned when there is one metric source instance. """
        MetricUnderTest.metric_source_class = metric_source.Birt
        metric_source_instance = metric_source.Birt(birt_url='http://birt')
        project = domain.Project(metric_sources={metric_source.Birt: metric_source_instance})
        product = domain.Product(metric_source_ids={metric_source_instance: 'birt id'})
        # pylint: disable=protected-access
        self.assertEqual('birt id', MetricUnderTest(project=project, subject=product)._metric_source_id)
        MetricUnderTest.metric_source_class = None

    def test_multiple_metric_sources(self):
        """ Test that the correct metric source id is returned when there are multiple metric source instances. """
        MetricUnderTest.metric_source_class = metric_source.Birt
        project = domain.Project(metric_sources={metric_source.Birt: ['Birt1', 'Birt2']})
        product = domain.Product(metric_source_ids={'Birt2': 'birt id'})
        # pylint: disable=protected-access
        self.assertEqual('birt id', MetricUnderTest(project=project, subject=product)._metric_source_id)
        MetricUnderTest.metric_source_class = None

    def test_no_matching_metric_source(self):
        """ Test that no metric source id is returned when there is no metric source instance for the product. """
        MetricUnderTest.metric_source_class = metric_source.Birt
        project = domain.Project(metric_sources={metric_source.Birt: ['Birt1']})
        product = domain.Product(metric_source_ids={'Birt2': 'birt id'})
        # pylint: disable=protected-access
        self.assertFalse(MetricUnderTest(project=project, subject=product)._metric_source_id)
        MetricUnderTest.metric_source_class = None

    def test_default_report(self):
        """ Test the default report. """
        self.assertEqual('FakeSubject heeft 0 foo.', self.__metric.report())

    def test_report_with_long_subject(self):
        """ Test that the subject is abbreviated when long. """
        self.assertEqual('FakeSubject heeft 0 foo.', self.__metric.report(max_subject_length=1))

    def test_report_with_perfect_template(self):
        """ Test that the subject is abbreviated when long. """
        self.__metric.perfect_template = 'Perfect!'
        self.__metric.perfect_value = 0
        self.assertEqual('Perfect!', self.__metric.report())

    def test_missing_metric_source_report(self):
        """ Test that the metric report explains which metric source needs to be configured. """
        # pylint: disable=attribute-defined-outside-init
        self.__metric.metric_source_class = metric_source.VersionControlSystem
        self.assertEqual('De subclass responsibility van FakeSubject kon niet gemeten worden omdat de bron '
                         'VersionControlSystem niet is geconfigureerd.', self.__metric.report())

    def test_missing_metric_source_id_report(self):
        """ Test that the metric report explains which metric source ids need to be configured. """
        project = domain.Project(metric_sources={metric_source.SystemTestReport: metric_source.JunitTestReport()})
        metric = MetricUnderTest(self.__subject, project=project)
        metric.metric_source_class = metric_source.SystemTestReport
        self.assertEqual('De subclass responsibility van FakeSubject kon niet gemeten worden omdat niet alle '
                         'benodigde bron-ids zijn geconfigureerd. Configureer ids voor de bron SystemTestReport.',
                         metric.report())

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

    def test_url(self):
        """ Test metric url when there is a metric source id. """
        mock_metric_source = MagicMock()
        mock_metric_source.metric_source_urls.return_value = ['http:/url1']
        mock_metric_source.metric_source_name = "Text"
        subject = MagicMock()
        subject.metric_source_id.return_value = "MsId"
        project = MagicMock()
        project.metric_sources.return_value = [mock_metric_source]
        test_metric = domain.Metric(subject=subject, project=project)

        self.assertEqual({"Text": "http:/url1"}, test_metric.url())

    def test_url_two_sources(self):
        """ Test metric url when there are two metric source ids. """
        mock_metric_source = MagicMock()
        mock_metric_source.metric_source_urls.return_value = ['http:/url1', 'http:/url2']
        mock_metric_source.metric_source_name = "Text"
        subject = MagicMock()
        subject.metric_source_id.return_value = "MsId"
        project = MagicMock()
        project.metric_sources.return_value = [mock_metric_source]
        test_metric = domain.Metric(subject=subject, project=project)

        self.assertEqual({"Text (1/2)": "http:/url1", "Text (2/2)": "http:/url2"}, test_metric.url())

    @patch.object(domain.Metric, '_get_display_urls')
    def test_url_from_metric_source_urls(self, mock_get_display_urls):
        """ Test metric url when there is no source id. """
        mock_metric_source = MagicMock()
        mock_metric_source.url.return_value = 'http://url!'
        mock_metric_source.metric_source_name = "Text"
        subject = MagicMock()
        subject.metric_source_id.return_value = "MsId"
        project = MagicMock()
        project.metric_sources.return_value = [mock_metric_source]
        mock_get_display_urls.return_value = None
        test_metric = domain.Metric(subject=subject, project=project)

        self.assertEqual({"Text": 'http://url!'}, test_metric.url())

    def test_url_metric_source_different_metric_source_urls(self):
        """ Test metric url when there are metric source urls. """
        mock_metric_source = MagicMock()
        mock_metric_source.metric_source_urls.return_value = ["metric source url"]
        mock_metric_source.metric_source_name = "Text"

        subject = MagicMock()
        subject.metric_source_id.return_value = "MsId"
        project = MagicMock()
        project.metric_sources.return_value = [mock_metric_source]
        test_metric = domain.Metric(subject=subject, project=project)

        self.assertEqual({"Text": "metric source url"}, test_metric.url())
        mock_metric_source.metric_source_urls.assert_called_once_with('MsId')

    def test_url_metric_source_different_display(self):
        """ Test metric url when there is a display link. """
        mock_metric_source = MagicMock()
        mock_metric_source.metric_source_urls.return_value = ["metric source url"]
        mock_metric_source.metric_source_name = "Text"

        subject = MagicMock()
        subject.metric_source_id.return_value = {"source": 'http:\\link', "display": 'http:\\display.url'}
        project = MagicMock()
        project.metric_sources.return_value = [mock_metric_source]
        test_metric = domain.Metric(subject=subject, project=project)

        self.assertEqual({"Text": "metric source url"}, test_metric.url())
        mock_metric_source.metric_source_urls.assert_called_once_with('http:\\display.url')

    def test_url_metric_source_different_display_two_links(self):
        """ Test metric url when there are two links - one with a display link and the other without. """
        mock_metric_source = MagicMock()
        mock_metric_source.metric_source_urls.return_value = ["metric source url"]
        mock_metric_source.metric_source_name = "Text"

        subject = MagicMock()
        subject.metric_source_id.return_value = [{"source": 'http:\\link', "display": 'http:\\display.url'}, "simple"]
        project = MagicMock()
        project.metric_sources.return_value = [mock_metric_source]
        test_metric = domain.Metric(subject=subject, project=project)

        self.assertEqual({"Text": "metric source url"}, test_metric.url())
        mock_metric_source.metric_source_urls.assert_called_once_with('http:\\display.url', "simple")

    def test_default_url(self):
        """ Test that the metric has no default url. """
        self.assertFalse(self.__metric.url())

    def test_default_url_label(self):
        """ Test that the metric has no default url label. """
        self.assertFalse(self.__metric.url_label_text)

    def test_recent_history_with_nones(self):
        """ Test that the metric has no history by default. """
        FakeHistory.values = [1.76, None, 2.02]
        self.assertEqual([2, None, 2], self.__metric.recent_history())

    @patch.object(metric_source.CompactHistory, 'get_dates')
    def test_get_recent_history_dates(self, mock_get_dates):
        """ Test that the metric calls appropriate function on history object and passes the result. """
        mock_get_dates.return_value = "whatever"
        project = MagicMock()
        project.metric_sources.return_value = [metric_source.CompactHistory]
        test_metric = domain.Metric(subject=MagicMock(), project=project)

        result = test_metric.get_recent_history_dates()

        mock_get_dates.assert_called_once()
        self.assertEqual("whatever", result)

    @patch.object(metric_source.CompactHistory, 'get_dates')
    def test_get_long_history_dates(self, mock_get_dates):
        """ Test that the metric calls appropriate function on history object and passes the result. """
        mock_get_dates.return_value = "whatever"
        project = MagicMock()
        project.metric_sources.return_value = [metric_source.CompactHistory]
        test_metric = domain.Metric(subject=MagicMock(), project=project)

        result = test_metric.get_long_history_dates()

        mock_get_dates.assert_called_once_with(long_history=True)
        self.assertEqual("whatever", result)

    @patch.object(metric_source.CompactHistory, 'recent_history')
    def test_recent_history(self, recent_history_mock):
        """ Test that the metric has no history by default. """
        recent_history_mock.return_value = [2.9]
        project = MagicMock()
        project.metric_sources.return_value = [metric_source.CompactHistory]
        test_metric = domain.Metric(subject=MagicMock(), project=project)

        self.assertEqual([3], test_metric.recent_history())

    @patch.object(metric_source.CompactHistory, 'long_history')
    def test_long_history(self, long_history_mock):
        """ Test that the metric has no history by default. """
        long_history_mock.return_value = [2.9]
        project = MagicMock()
        project.metric_sources.return_value = [metric_source.CompactHistory]
        test_metric = domain.Metric(subject=MagicMock(), project=project)

        self.assertEqual([3], test_metric.long_history())

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
        self.assertFalse(self.__metric.comment_url_label_text)

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

    def test_adapted_target_comment(self):
        """ Test that the metric comment mentions that the target has been adapted. """
        # pylint: disable=attribute-defined-outside-init
        self.__subject.low_target = lambda subject: 'Subject specific target'
        self.assertEqual("De norm is aangepast van Subclass responsibility foo (default) naar Subject specific "
                         "target foo.", self.__metric.comment())

    def test_debt_and_adapted_target_comment(self):
        """ Test that the metric comment mentions both debt and adapted target. """
        # pylint: disable=attribute-defined-outside-init
        self.__subject.debt_target = domain.TechnicalDebtTarget(10, 'Debt.')
        self.__subject.low_target = lambda subject: 'Subject specific target'
        self.assertEqual("De norm is aangepast van Subclass responsibility foo (default) naar Subject specific "
                         "target foo. De op dit moment geaccepteerde technische schuld is 10 foo. Debt.",
                         self.__metric.comment())

    def test_numerical_value(self):
        """ Test that the numerical value is the value by default. """
        self.assertEqual(self.__metric.numerical_value(), 0)

    @patch.object(MetricUnderTest, 'value')
    def test_numerical_value_when_returns_tuple(self, value_mock):
        """ Test that the numerical value is the value by default. """
        value_mock.return_value = (3, {})
        self.assertEqual(self.__metric.numerical_value(), 3)

    @patch.object(MetricUnderTest, 'value')
    def test_numerical_value_when_returns_dict(self, value_mock):
        """ Test that the numerical value is the value by default. """
        value_mock.return_value = ({}, {})
        self.assertRaises(NotImplementedError, self.__metric.numerical_value)

    def test_status_start_date(self):
        """ Test that the metric gets the start date of the status from the history. """
        self.assertEqual(datetime.datetime(2013, 1, 1, 10, 0, 0), self.__metric.status_start_date())

    def test_convert_item_to_extra_info_none(self):
        """ Test that method returns the same item it got. """
        item = object()
        self.assertEqual(item, self.__metric.convert_item_to_extra_info(item))

    @patch.object(domain.Metric, 'extra_info_rows')
    def test_extra_info(self, mock_extra_info_rows):
        """ Test that extra_info, as a base class function, returns None. """
        mock_extra_info_rows.return_value = [('VAL1', 'VAL2')]
        project = MagicMock()
        project.metric_sources.return_value = [MagicMock()]
        metric = domain.Metric(subject=MagicMock(), project=project)
        metric.extra_info_headers = {"col1": "Col 1", "col2": "Col 2"}

        result = metric.extra_info()

        self.assertEqual(domain.ExtraInfo(col1="Col 1", col2="Col 2").headers, result.headers)
        self.assertEqual([{"col1": "VAL1", "col2": "VAL2"}], result.data)

    @patch.object(domain.Metric, 'extra_info_rows')
    def test_extra_info_for_no_urls(self, mock_extra_info_rows):
        """ Test that extra info is None when there are no jobs' urls. """
        mock_extra_info_rows.return_value = []

        self.assertEqual(None, self.__metric.extra_info())

    def test_extra_info_rows(self):
        """ Test that the default list of urls is empty. """
        self.assertEqual(list(), self.__metric.extra_info_rows())


class MetricStatusTest(unittest.TestCase):
    """ Test case for the Metric domain class status method. """

    def setUp(self):
        self.__subject = FakeSubject()
        self.__project = domain.Project()
        self.__metric = MetricUnderTest(self.__subject, project=self.__project)

    def assert_status(self, expected_status, metric=None):
        """ Assert that the metric has the expected status. """
        metric = metric or self.__metric
        self.assertEqual(expected_status, metric.status())

    def test_default_status(self):
        """ Test that the default status is green. """
        self.assert_status('green')

    def test_missing_metric_sources_status(self):
        """ Test that the status is missing metric sources when the project doesn't have the required metric source. """
        # pylint: disable=attribute-defined-outside-init
        self.__metric.metric_source_class = metric_source.VersionControlSystem
        self.assert_status('missing_source')

    def test_missing_metric_source_id_status(self):
        """ Test that the status is missing metric sources when the subject doesn't have the required metric source
            id. """
        project = domain.Project(metric_sources={metric_source.SystemTestReport: metric_source.JunitTestReport()})
        metric = MetricUnderTest(self.__subject, project=project)
        metric.metric_source_class = metric_source.SystemTestReport
        self.assert_status('missing_source', metric)

    def test_missing_metric(self):
        """ Test that the metric status is missing when the value is -1. """
        self.__metric.value_to_return = -1
        self.assert_status('missing')

    def test_perfect_status(self):
        """ Test that the status is perfect when the value equals the perfect target. """
        self.__metric.perfect_value = 0  # pylint: disable=attribute-defined-outside-init
        self.assert_status('perfect')


class ExtraInfoTest(unittest.TestCase):
    """ Test extra info functionality. """

    def test_header_created(self):
        """ Test that header dictionary is correctly created."""
        extra_info = domain.ExtraInfo(col1="Col 1 Header", col2="Col 2 Header")
        self.assertEqual({"col1": "Col 1 Header", "col2": "Col 2 Header"}, extra_info.headers)

    def test_row_added(self):
        """ Test that metric data is correctly created."""
        extra_info = domain.ExtraInfo(col1="", col2="")
        extra_info += "val1", {"href": "http://url", "text": "Description"}
        self.assertEqual([{"col1": "val1", "col2": {"href": "http://url", "text": "Description"}}], extra_info.data)

    def test_row_of_single_elment_added(self):
        """ Test that metric data is correctly created."""
        extra_info = domain.ExtraInfo(col2="")
        extra_info += {"href": "http://url", "text": "Description"}
        self.assertEqual([{"col2": {"href": "http://url", "text": "Description"}}], extra_info.data)

    def test_rows_added(self):
        """ Test that metric data is correctly created."""
        extra_info = domain.ExtraInfo(col1="", col2="")
        extra_info += "val1", {"href": "http://url", "text": "Description"}, \
                      "val3", {"href": "http://url3", "text": "Description3"}
        self.assertEqual([{"col1": "val1", "col2": {"href": "http://url", "text": "Description"}},
                          {"col1": "val3", "col2": {"href": "http://url3", "text": "Description3"}}], extra_info.data)

    def test_serialization(self):
        """ Test that metric data is correctly json serialized."""
        extra_info = domain.ExtraInfo(col1="C1", col2="C2")
        extra_info += "val1", {"href": "http://url", "text": "Description"}
        extra_info.title = "Title"

        result = json.dumps(extra_info.__dict__)
        self.assertEqual('{"headers": {"col1": "C1", "col2": "C2"}, "title": "Title", '
                         '"data": [{"col1": "val1", "col2": {"href": "http://url", "text": "Description"}}]}', result)
