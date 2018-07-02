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
from unittest.mock import MagicMock
from hqlib import domain, metric_source
from hqlib.metric.environment import CIJobs


class CIJobsTest(unittest.TestCase):
    """ Unit tests for the failing CI jobs metric. """

    def setUp(self):
        """ Create the text fixture. """
        self._jenkins = MagicMock()
        self._jenkins.url.return_value = 'mock_jenkins_url'
        self._jenkins.metric_source_name = 'link'
        self._project = domain.Project(metric_sources={metric_source.CIServer: self._jenkins},
                                       metric_source_ids={self._jenkins: 'dummy'})
        self._metric = CIJobs(subject=self._project, project=self._project)

    def test_label(self):
        """ Test that the label to use in the HTML report is correct. """
        self.assertEqual('', self._metric.url_label_text)

    def test_url(self):
        """ Test if ci job returns correct url. """
        self.assertEqual({"link": "mock_jenkins_url"}, self._metric.url())

    def test_url_empty(self):
        """ Test if ci job returns empty url when metric source is empty. """
        self._project = domain.Project(metric_sources={metric_source.CIServer: []})
        self._metric = CIJobs(subject=self._project, project=self._project)
        self.assertEqual({}, self._metric.url())

    def test_convert_item_to_extra_info(self):
        """ Test if ci job item is correctly converted to extra info record. """
        expected = ({'href': 'http://xx.xl', 'text': 'Link Text'}, '42')

        result = self._metric.convert_item_to_extra_info(('Link Text', 'http://xx.xl', '42'))

        self.assertEqual(expected, result)

    def test_convert_item_to_extra_info_none(self):
        """ Test if ci job item is correctly converted to extra info record. """

        result = self._metric.convert_item_to_extra_info(())

        self.assertEqual(None, result)
