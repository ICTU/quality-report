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
from unittest.mock import patch, MagicMock
from hqlib import domain, metric_source
from hqlib.metric.environment import CIJobs


class CIJobsTest(unittest.TestCase):
    """ Unit tests for the failing CI jobs metric. """

    def setUp(self):
        """ Create the text fixture. """
        self._jenkins = MagicMock()
        self._project = domain.Project(metric_sources={metric_source.CIServer: self._jenkins},
                                       metric_source_ids={self._jenkins: 'dummy'})
        self._metric = CIJobs(subject=self._project, project=self._project)

    def test_format_text_with_links(self):
        """ Function returns unchanged text. """
        self.assertEqual("Some text... ", self._metric.format_text_with_links(text="Some text... "))

    def test_format_text_with_links_escape(self):
        """ Function returns text with html escaped characters. """
        self.assertEqual("Some &amp;text... ", self._metric.format_text_with_links(text="Some &text... "))

    def test_format_text_with_links_escape_(self):
        """ Function returns text with html escaped characters. """
        self.assertEqual("Some &amp;text... ", self._metric.format_text_with_links(text="Some &text... "))

    def test_url(self):
        """ Test that the url of the metric equals the url of Jenkins. """
        self.assertEqual(dict(), self._metric.url())

    def test_label(self):
        """ Test that the label to use in the HTML report is correct. """
        self.assertEqual('', self._metric.url_label_text)

    def test_extra_info_is_none(self):
        """ Test that extra info is None when there is no metric source """
        self._metric._metric_source = None
        self.assertEqual(None, self._metric.extra_info())

    @patch.object(CIJobs, '_jobs_url')
    def test_extra_info(self, mock_jobs_url):
        """ Test that extra info is correct. """
        mock_jobs_url.return_value = [('name', 'http://url', '7')]
        expected_extra_info = domain.ExtraInfo(link="Job naam", comment="Aantal dagen ")
        expected_extra_info += {'href': 'http://url', 'text': 'name'}, '7'

        result = self._metric.extra_info()
        self.assertEqual(expected_extra_info.headers, result.headers)
        self.assertEqual(expected_extra_info.data, result.data)

    @patch.object(CIJobs, '_jobs_url')
    def test_extra_info_for_no_urls(self, mock_jobs_url):
        """ Test that extra info is None when there are no jobs' urls. """
        mock_jobs_url.return_value = []

        self.assertEqual(None, self._metric.extra_info())
