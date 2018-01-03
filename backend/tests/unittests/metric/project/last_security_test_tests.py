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

from hqlib import domain, metric, metric_source


class ProjectAndFileWithDatePrerequisitesTestCase(unittest.TestCase):
    """" Prerequisites tests for LastSecurityTestCase"""

    def test_project_and_file_with_date(self):
        """" Checks if the real objects fulfill requirements expected by LastSecurityTestCase """

        project = domain.Project(metric_sources={metric_source.FileWithDate: metric_source.FileWithDate()})

        fwd = project.metric_sources(metric_source.FileWithDate)[0]

        self.assertTrue(project is not None)
        self.assertTrue(fwd is not None)
        self.assertTrue(callable(getattr(fwd, "get_datetime_from_content")))


@patch('hqlib.domain.Project')
class LastSecurityTestCase(unittest.TestCase):
    """ Unit tests for the last security test period metric. """

    def test_value(self, project_mock):
        """ Test that the value of the metric equals the period from last security test in days. """

        fake_url = 'http://fake_url'
        file_with_date = MagicMock()
        project_mock.metric_sources.return_value = [file_with_date]
        file_with_date.get_datetime_from_content.return_value = datetime.datetime.now() - datetime.timedelta(2)

        subject_mock = MagicMock()
        subject_mock.metric_source_id.return_value = fake_url
        last_security_test = metric.LastSecurityTest(subject=subject_mock, project=project_mock)

        result = last_security_test.value()

        file_with_date.get_datetime_from_content.assert_called_once_with(fake_url)
        self.assertEqual(2, result)

    def test_value_slightly_newer(self, project_mock):
        """ Test that the value of the metric is 0 when last test happens to have a slightly newer date
            (due to server time)."""

        fake_url = 'http://fake_url'
        file_with_date = MagicMock()
        project_mock.metric_sources.return_value = [file_with_date]
        file_with_date.get_datetime_from_content.return_value = datetime.datetime.now() + datetime.timedelta(seconds=5)

        subject_mock = MagicMock()
        subject_mock.metric_source_id.return_value = fake_url
        last_security_test = metric.LastSecurityTest(subject=subject_mock, project=project_mock)

        result = last_security_test.value()

        file_with_date.get_datetime_from_content.assert_called_once_with(fake_url)
        self.assertEqual(0, result)

    def test_value_newer(self, project_mock):
        """ Test that the value of the metric is -1 when last test has a date in the future."""

        fake_url = 'http://fake_url'
        file_with_date = MagicMock()
        project_mock.metric_sources.return_value = [file_with_date]
        file_with_date.get_datetime_from_content.return_value = datetime.datetime.now() + datetime.timedelta(days=5)

        subject_mock = MagicMock()
        subject_mock.metric_source_id.return_value = fake_url
        last_security_test = metric.LastSecurityTest(subject=subject_mock, project=project_mock)

        result = last_security_test.value()

        file_with_date.get_datetime_from_content.assert_called_once_with(fake_url)
        self.assertEqual(-1, result)

    def test_value_invalid(self, project_mock):
        """ Test that the value returns -1 when last security happens to min date . """

        fake_url = 'http://fake_url'
        file_with_date = MagicMock()
        project_mock.metric_sources.return_value = [file_with_date]
        file_with_date.get_datetime_from_content.return_value = datetime.datetime.min

        subject_mock = MagicMock()
        subject_mock.metric_source_id.return_value = fake_url
        last_security_test = metric.LastSecurityTest(subject=subject_mock, project=project_mock)

        result = last_security_test.value()

        file_with_date.get_datetime_from_content.assert_called_once_with(fake_url)
        self.assertEqual(-1, result)

    def test_value_without_metric_source(self, project_mock):
        """ Test that the value returns -1 when there is no metric source. """

        project_mock.metric_sources = MagicMock()
        project_mock.metric_sources.return_value = []

        last_security_test = metric.LastSecurityTest(subject=None, project=project_mock)

        result = last_security_test.value()

        self.assertEqual(-1, result)

    def test_value_without_metric_source_id(self, project_mock):
        """ Test that the value returns -1 when there is no metric source id is None. """

        fake_url = None
        file_with_date = MagicMock()
        project_mock.metric_sources.return_value = [file_with_date]
        file_with_date.get_datetime_from_content.return_value = datetime.datetime.now()

        subject_mock = MagicMock()
        subject_mock.metric_source_id.return_value = fake_url
        last_security_test = metric.LastSecurityTest(subject=subject_mock, project=project_mock)

        result = last_security_test.value()

        self.assertFalse(file_with_date.get_datetime_from_content.called)
        self.assertEqual(-1, result)
