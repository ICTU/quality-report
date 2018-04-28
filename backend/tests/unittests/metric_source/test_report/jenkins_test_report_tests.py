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
from unittest.mock import patch
import urllib.error

from hqlib.metric_source import JenkinsTestReport, Jenkins, UrlOpener


class JenkinsTestReportTest(unittest.TestCase):
    """ Unit tests for the Jenkins test report class. """
    def setUp(self):
        for method in (JenkinsTestReport.datetime, JenkinsTestReport.failed_tests, JenkinsTestReport.skipped_tests,
                       JenkinsTestReport.passed_tests):
            method.cache_clear()

    @patch.object(Jenkins, "jobs")
    @patch.object(UrlOpener, "url_read")
    def test_testreport(self, mock_url_read, mock_jenkins_jobs):
        """ Test retrieving a Jenkins test report. """
        mock_jenkins_jobs.return_value = [{"name": "job"}]
        mock_url_read.return_value = '{"timestamp":1467929105000, "actions":[{"urlName":"testReport", "failCount":2, ' \
                                     '"passCount":9, "skipCount":1, "totalCount":12}]}'
        jenkins = JenkinsTestReport(url="http://jenkins")
        self.assertEqual(2, jenkins.failed_tests('job'))
        self.assertEqual(9, jenkins.passed_tests('job'))
        self.assertEqual(1, jenkins.skipped_tests('job'))

    @patch.object(Jenkins, "jobs")
    @patch.object(UrlOpener, "url_read")
    def test_testreport_with_re(self, mock_url_read, mock_jenkins_jobs):
        """ Test retrieving a Jenkins test report. """
        mock_jenkins_jobs.return_value = [{"name": "job1"}, {"name": "job2"}, {"name": "ignore"}]
        mock_url_read.return_value = '{"timestamp":1467929105000, "actions":[{"urlName":"testReport", "failCount":2, ' \
                                     '"passCount":9, "skipCount":1, "totalCount":12}]}'
        jenkins = JenkinsTestReport(url="http://jenkins")
        self.assertEqual(4, jenkins.failed_tests('job?'))
        self.assertEqual(18, jenkins.passed_tests('job?'))
        self.assertEqual(2, jenkins.skipped_tests('job?'))

    @patch.object(Jenkins, "jobs")
    @patch.object(UrlOpener, "url_read")
    def test_testreport_without_pass_count(self, mock_url_read, mock_jenkins_jobs):
        """ Test retrieving a Jenkins test report that has no pass count. Apparently that field is not present when
            there are no tests. """
        mock_jenkins_jobs.return_value = [{"name": "job"}]
        mock_url_read.return_value = '{"timestamp":1467929105000, "actions":[{"urlName":"testReport", ' \
                                     '"failCount":0, "skipCount":0, "totalCount":8}]}'
        jenkins = JenkinsTestReport(url="http://jenkins")
        self.assertEqual(0, jenkins.failed_tests('job'))
        self.assertEqual(8, jenkins.passed_tests('job'))
        self.assertEqual(0, jenkins.skipped_tests('job'))

    @patch.object(Jenkins, "jobs")
    @patch.object(UrlOpener, "url_read")
    def test_last_completed_build_without_results(self, mock_url_read, mock_jenkins_jobs):
        """ Test retrieving a Jenkins test report that was completed but has no test results, e.g. because it was
            aborted. """
        mock_jenkins_jobs.return_value = [{"name": "job"}]
        mock_url_read.side_effect = [
            '{"timestamp": 1467929105000, "actions":[]}',
            '{"timestamp": 1467929105000, "actions":[{}, {"totalCount":10, "failCount":1}]}']
        jenkins = JenkinsTestReport(url="http://jenkins")
        self.assertEqual(1, jenkins.failed_tests("job"))

    @patch.object(Jenkins, "jobs")
    @patch.object(UrlOpener, "url_read")
    def test_http_error(self, mock_url_read, mock_jenkins_jobs):
        """ Test that the default is returned when a HTTP error occurs. """
        mock_jenkins_jobs.return_value = [{"name": "job"}]
        mock_url_read.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        jenkins = JenkinsTestReport(url="http://jenkins")
        self.assertEqual(-1, jenkins.failed_tests('raise'))
        self.assertEqual(-1, jenkins.passed_tests('raise'))
        self.assertEqual(-1, jenkins.skipped_tests('raise'))

    @patch.object(Jenkins, "jobs")
    @patch.object(UrlOpener, "url_read")
    def test_eval_exception(self, mock_url_read, mock_jenkins_jobs):
        """ Test that the default is returned when the json can't be parsed. """
        mock_jenkins_jobs.return_value = [{"name": "job"}]
        mock_url_read.return_value = '{"failCount":, "passCount":9, "skipCount":1}'
        jenkins = JenkinsTestReport(url="http://jenkins")
        self.assertEqual(-1, jenkins.failed_tests('job'))

    @patch.object(Jenkins, "jobs")
    @patch.object(UrlOpener, "url_read")
    def test_report_datetime(self, mock_url_read, mock_jenkins_job):
        """ Test that the date and time of the test suite is returned. """
        mock_jenkins_job.return_value = [{"name": "job"}]
        mock_url_read.return_value = '{"timestamp":1467929105000, "actions":[{"totalCount":10,"failCount":0}]}'
        jenkins = JenkinsTestReport(url="http://jenkins")
        self.assertEqual(datetime.datetime.fromtimestamp(1467929105000 / 1000.), jenkins.datetime('job'))

    @patch.object(Jenkins, "jobs")
    @patch.object(UrlOpener, "url_read")
    def test_report_datetime_on_missing_results(self, mock_url_read, mock_jenkins_jobs):
        """ Test that the date and time of the test suite is returned, even when the last completed build has no
            test results. """
        mock_jenkins_jobs.return_value = [{"name": "job"}]
        mock_url_read.side_effect = ['{"timestamp":"this build should be ignored"}',
                                     '{"actions":[{"totalCount":10,"failCount":0}], "timestamp":1467929105000}']
        jenkins = JenkinsTestReport(url="http://jenkins")
        self.assertEqual(datetime.datetime.fromtimestamp(1467929105000 / 1000.), jenkins.datetime('job'))

    @patch.object(Jenkins, "jobs")
    @patch.object(UrlOpener, "url_read")
    def test_missing_report_datetime(self, mock_url_read, mock_jenkins_jobs):
        """ Test that the minimum datetime is returned when the date and time of the test suite is missing. """
        mock_jenkins_jobs.return_value = [{"name": "job"}]
        mock_url_read.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        jenkins = JenkinsTestReport(url="http://jenkins")
        self.assertEqual(datetime.datetime.min, jenkins.datetime('job'))

    @patch.object(Jenkins, "jobs")
    @patch.object(UrlOpener, "url_read")
    def test_invalid_date_time(self, mock_url_read, mock_jenkins_jobs):
        """ Test that the minimum datetime is returned when the json invalid. """
        mock_jenkins_jobs.return_value = [{"name": "job"}]
        mock_url_read.return_value = '{"timestamp":}'
        jenkins = JenkinsTestReport(url="http://jenkins")
        self.assertEqual(datetime.datetime.min, jenkins.datetime("job"))

    @patch.object(Jenkins, "jobs")
    def test_date_time_on_timeout(self, mock_jenkins_jobs):
        """ Test that the minimum datetime is returned when the Jenkins jobs method gives a timeout. """
        mock_jenkins_jobs.side_effect = TimeoutError
        jenkins = JenkinsTestReport(url="http://jenkins")
        self.assertEqual(datetime.datetime.min, jenkins.datetime("job"))

    def test_url(self):
        """ Test the metric sourc url. """
        jenkins = JenkinsTestReport(url="http://jenkins")
        self.assertEqual("http://jenkins/", jenkins.url())

    @patch.object(Jenkins, "jobs")
    def test_metric_source_urls(self, mock_jenkins_jobs):
        """ Test that the metric source urls are assembled correctly. """
        mock_jenkins_jobs.return_value = [{"name": "job1"}, {"name": "master"}, {"name": "test1"}, {"name": "test2"}]
        jenkins = JenkinsTestReport(url="http://jenkins")
        self.assertEqual(["http://jenkins/job/job1", "http://jenkins/job/pipeline/job/master",
                          "http://jenkins/job/test1", "http://jenkins/job/test2"],
                         jenkins.metric_source_urls("job1", "pipeline/job/master", "test?"))

    @patch.object(Jenkins, "jobs")
    def test_metric_source_urls__timeout(self, mock_jenkins_jobs):
        """ Test that the metric source urls are assembled correctly. """
        mock_jenkins_jobs.side_effect = TimeoutError
        jenkins = JenkinsTestReport(url="http://jenkins")
        self.assertEqual(["http://jenkins/job/job1", "http://jenkins/job/pipeline/job/master",
                          "http://jenkins/job/test?"],
                         jenkins.metric_source_urls("job1", "pipeline/job/master", "test?"))

    @patch.object(Jenkins, "jobs")
    def test_metric_source_urls_no_match(self, mock_jenkins_jobs):
        """ Test that the metric source urls are assembled correctly. """
        mock_jenkins_jobs.return_value = [{"name": "job1"}, {"name": "master"}, {"name": "test1"}, {"name": "test2"}]
        jenkins = JenkinsTestReport(url="http://jenkins")
        self.assertEqual(["http://jenkins/job/notfound.*"], jenkins.metric_source_urls("notfound.*"))
