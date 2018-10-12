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
from hqlib.domain.measurement.metric_source_with_issues import MetricSourceWithIssues


class MetricSourceWithIssuesTests(unittest.TestCase):
    """ Unit tests for the metric source domain class. """

    def test_issues(self):
        """ Test that metric source has an empty issues list. """
        self.assertEqual([], MetricSourceWithIssues().issues())

    def test_issue_class(self):
        """ Test that metric source has an Issue class . """
        issue = MetricSourceWithIssues.Issue('title')
        self.assertIsNotNone(issue)
        self.assertEqual('title', issue.title)
