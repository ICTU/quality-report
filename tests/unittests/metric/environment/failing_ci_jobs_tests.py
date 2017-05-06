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

from hqlib import metric, domain, metric_source


class FakeJenkins(object):
    """ Fake Jenkins instance for testing purposes. """
    # pylint: disable=unused-argument
    needs_metric_source_id = metric_source.Jenkins.needs_metric_source_id

    @classmethod
    def failing_jobs_url(cls, *args):
        """ Return the url(s) of the failing job(s). """
        return {'job_name (3 dagen)': 'http://jenkins/job_name'}

    @staticmethod
    def number_of_active_jobs(*args):
        """ Return the total number of active CI jobs. """
        return 2


class FailingCIJobsTest(unittest.TestCase):
    """ Unit tests for the failing CI jobs metric. """

    expected_report = '1 van de 2 actieve CI-jobs faalt.'

    def setUp(self):
        """ Create the text fixture. """
        self._subject = None
        self._project = domain.Project(metric_sources={metric_source.Jenkins: FakeJenkins()})
        self._metric = metric.FailingCIJobs(subject=self._subject, project=self._project)

    def test_norm_template_default_values(self):
        """ Test that the right values are returned to fill in the norm template. """
        self.assertTrue(metric.FailingCIJobs.norm_template % metric.FailingCIJobs.norm_template_default_values())

    def test_value(self):
        """ Test that the value equals the number of failing jobs. """
        self.assertEqual(1, self._metric.value())

    def test_url(self):
        """ Test that the url of the metric equals the url of Jenkins. """
        self.assertEqual(FakeJenkins().failing_jobs_url(), self._metric.url())

    def test_report(self):
        """ Test the metric report. """
        self.assertEqual(self.expected_report, self._metric.report())

    def test_label(self):
        """ Test that the label to use in the HTML report is correct. """
        self.assertEqual('Falende jobs', self._metric.url_label_text)
