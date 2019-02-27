"""
Copyright 2012-2019 Ministerie van Sociale Zaken en Werkgelegenheid

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
import logging
import urllib.error
import unittest
from unittest.mock import patch
from hqlib.metric_source import Jenkins, url_opener
from hqlib.typing import DateTime


def to_jenkins_timestamp(date_time: DateTime, epoch: DateTime = datetime.datetime(1970, 1, 1)) -> int:
    """ Convert datetime instance to *milli*seconds since epoch. """
    delta = date_time - epoch
    return (delta.microseconds + (delta.seconds + delta.days * 24 * 3600) * 10**6) / 1000


@patch.object(url_opener.UrlOpener, 'url_read')
class JenkinsTest(unittest.TestCase):
    """ Unit tests for the Jenkins class. """

    def setUp(self):
        self.__jenkins = Jenkins('http://jenkins/', 'username', 'password')

    def test_no_failing_jobs(self, mock_url_read):
        """ Test the number of failing jobs when there are no failing jobs. """
        mock_url_read.side_effect = ['{"jobs":[{"_class":"cls", "name":"_", "url":"http://?", "color":"blue"}]}',
                                     '{}',
                                     '{"jobs":[{"_class":"", "name":"_", "url":"http://?", "color":"blue"}]}']
        self.assertEqual(0, self.__jenkins.number_of_failing_jobs())
        self.assertEqual(mock_url_read.call_count, 2)

    def test_no_failing_jobs_url(self, mock_url_read):
        """ Test the number of failing jobs when there are no failing jobs. """
        mock_url_read.side_effect = ['{"jobs":[{"_class":"cls", "name":"_", "url":"http://?", "color":"blue"}]}',
                                     '{}',
                                     '{"jobs":[{"_class":"", "name":"_", "url":"http://?", "color":"blue"}]}']
        self.assertEqual([], self.__jenkins.failing_jobs_url())

    def test_one_failing_job(self, mock_url_read):
        """ Test the failing jobs with one failing job. """
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"proj-pipeline","url":"http://jenkins.proj/job/proj-pipeline/"}]}',
            '{"jobs":[{"description":None,"name":"_","url":"http://jenkins.proj/","buildable":True,"color":"red"}]}',
            '{}',
            '{"builds":[{"result":"FAILURE"}]}']

        self.assertEqual(1, self.__jenkins.number_of_failing_jobs())

    def test_one_failing_job_url(self, mock_url_read):
        """ Test the failing jobs with one failing job. """
        date_time = datetime.datetime(2013, 4, 1, 12, 0, 0)
        mock_url_read.side_effect = [
            b'{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            '{"jobs":[{"name":"job1","url":"http://jenkins/project-x/job/job1","buildable":True,"color":"red"}]}',
            '{}',
            '{"builds":[{"result":"SUCCESS"},{"result":"FAILURE"}]}',
            '{"building":False,"result":"SUCCESS","timestamp":' + str(int(to_jenkins_timestamp(date_time))) + '}']

        expected_days_ago = (datetime.datetime.utcnow() - date_time).days
        self.assertEqual([('project-x/job1', 'http://jenkins/project-x/job/job1', '{0:d}'.format(expected_days_ago))],
                         self.__jenkins.failing_jobs_url())

    @patch.object(logging, 'error')
    def test_failing_jobs_url_eval_error(self, mock_error, mock_url_read):
        """ Test the failing jobs with one failing job. """
        mock_url_read.side_effect = ['{ "jobs": ??? }']

        self.assertRaises(SyntaxError, Jenkins('http://jenkins/', 'username', 'password').failing_jobs_url)
        self.assertEqual("Couldn't evaluate %s from %s: %s", mock_error.call_args_list[0][0][0])
        self.assertEqual('{ "jobs": ??? }', mock_error.call_args_list[0][0][1])

    @patch.object(logging, 'warning')
    def test_failing_jobs_url_key_error(self, mock_warning, mock_url_read):
        """ Test that the failing job is returned if no timestamp key found. """
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            '{"jobs":[{"name":"job1","url":"http://jenkins/project-x/job/job1","buildable":True,"color":"red"}]}',
            '{}',
            '{"builds":[{"result":"SUCCESS"},{"result":"FAILURE"}]}',
            '{"building":False,"result":"SUCCESS","x-timestamp": "x"}']

        self.assertEqual([('project-x/job1', 'http://jenkins/project-x/job/job1', '?')],
                         self.__jenkins.failing_jobs_url())
        self.assertEqual("Couldn't get timestamp from %s: %s.", mock_warning.call_args_list[0][0][0])
        self.assertEqual(
            "http://jenkins/project-x/job/job1/lastStableBuild/api/python", mock_warning.call_args_list[0][0][1])
        self.assertIsInstance(mock_warning.call_args_list[0][0][2], KeyError)

    @patch.object(logging, 'warning')
    def test_failing_jobs_url_value_error(self, mock_warning, mock_url_read):
        """ Test that the failing job is returned if invalid timestamp key found. """
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            '{"jobs":[{"name":"job1","url":"http://jenkins/project-x/job/job1","buildable":True,"color":"red"}]}',
            '{}',
            '{"builds":[{"result":"SUCCESS"},{"result":"FAILURE"}]}',
            '{"building":False,"result":"SUCCESS","timestamp": "x-no-timestamp"}']

        self.assertEqual([('project-x/job1', 'http://jenkins/project-x/job/job1', '?')],
                         self.__jenkins.failing_jobs_url())
        self.assertEqual("Couldn't get timestamp from %s: %s.", mock_warning.call_args_list[0][0][0])
        self.assertEqual("http://jenkins/project-x/job/job1/lastStableBuild/api/python",
                         mock_warning.call_args_list[0][0][1])
        self.assertIsInstance(mock_warning.call_args_list[0][0][2], ValueError)

    def test_one_failing_job_url_ending_with_slash(self, mock_url_read):
        """ Test the failing jobs with one failing job. """
        date_time = datetime.datetime(2013, 4, 1, 12, 0, 0)
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            '{"jobs":[{"name":"job1","url":"http://jenkins/project-x/job/job1/","buildable":True,"color":"red"}]}',
            '{}',
            '{"builds":[{"result":"SUCCESS"},{"result":"FAILURE"}]}',
            '{"building":False,"result":"SUCCESS","timestamp":' + str(int(to_jenkins_timestamp(date_time))) + '}']

        expected_days_ago = (datetime.datetime.utcnow() - date_time).days
        self.assertEqual([('project-x/job1', 'http://jenkins/project-x/job/job1/', '{0:d}'.format(expected_days_ago))],
                         self.__jenkins.failing_jobs_url())

    def test_one_failing_job_url_with_different_name(self, mock_url_read):
        """ Test the failing jobs with the job having the name different than in the url. """
        date_time = datetime.datetime(2013, 4, 1, 12, 0, 0)
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            '{"jobs":[{"name":"real_name","url":"http://jenkins/project-x/job/job1/","buildable":True,"color":"red"}]}',
            '{}',
            '{"builds":[{"result":"SUCCESS"},{"result":"FAILURE"}]}',
            '{"building":False,"result":"SUCCESS","timestamp":' + str(int(to_jenkins_timestamp(date_time))) + '}']

        expected_days_ago = (datetime.datetime.utcnow() - date_time).days
        self.assertEqual([('real_name', 'http://jenkins/project-x/job/job1/', '{0:d}'.format(expected_days_ago))],
                         self.__jenkins.failing_jobs_url())

    def test_one_failing_job_url_with_unexpected_url(self, mock_url_read):
        """ Test the failing jobs with the job having the 'job' part omitted from the url. """
        date_time = datetime.datetime(2013, 4, 1, 12, 0, 0)
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            '{"jobs":[{"name":"job1","url":"http://jenkins/project-x/xjobx/job1/","buildable":True,"color":"red"}]}',
            '{}',
            '{"builds":[{"result":"SUCCESS"},{"result":"FAILURE"}]}',
            '{"building":False,"result":"SUCCESS","timestamp":' + str(int(to_jenkins_timestamp(date_time))) + '}']

        expected_days_ago = (datetime.datetime.utcnow() - date_time).days
        self.assertEqual([('job1', 'http://jenkins/project-x/xjobx/job1/', '{0:d}'.format(expected_days_ago))],
                         self.__jenkins.failing_jobs_url())

    def test_ignore_disabled_job(self, mock_url_read):
        """ Test that disabled failing jobs are ignored. """
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            '{"jobs":[{"name":"job1","url":"http://jenkins/job/job1/","buildable":False,"color":"red"}]}',
            '{}']
        self.assertEqual([], self.__jenkins.failing_jobs_url())

    def test_ignore_pipelines(self, mock_url_read):
        """ Test that pipelines (jobs without buildable flag) are ignored. """
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            '{"jobs":[{"name":"job1","url":"http://jenkins/job/job1/","color":"red"}]}',
            '{}']
        self.assertEqual([], self.__jenkins.failing_jobs_url())

    def test_include_pipeline_job(self, mock_url_read):
        """ Test that pipeline jobs are included. """
        timestamp = to_jenkins_timestamp(datetime.datetime.utcnow() - datetime.timedelta(days=100))
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            '{"jobs":[{"name":"master","url":"http://jenkins/job/master/","buildable":True,"color":"red"}]}',
            '{}',
            '{"builds":[{"result":"SUCCESS"},{"result":"FAILURE"}]}',
            '{"building":False,"result":"SUCCESS","timestamp":' + str(int(timestamp)) + '}']

        self.assertEqual([('jenkins/master', 'http://jenkins/job/master/', '100')], self.__jenkins.failing_jobs_url())

    def test_failing_jobs_url_not_old_job(self, mock_url_read):
        """ Test that a job failing for less than one day are not considered. """
        timestamp = to_jenkins_timestamp(datetime.datetime.utcnow() - datetime.timedelta(hours=23))
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            '{"jobs":[{"name":"master","url":"http://jenkins/job/master/","buildable":True,"color":"red"}]}',
            '{"builds":[{"result":"SUCCESS"},{"result":"FAILURE"}]}',
            '{"building":False,"result":"SUCCESS","timestamp":' + str(int(timestamp)) + '}']

        self.assertEqual([], self.__jenkins.failing_jobs_url())

    def test_failing_jobs_url(self, mock_url_read):
        """ Test that the failing jobs url dictionary contains the url for the failing job. """
        timestamp = to_jenkins_timestamp(datetime.datetime.utcnow() - datetime.timedelta(days=100))
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            '{"jobs":[{"name":"job1","url":"http://jenkins/job/job1/","buildable":True,"color":"red"}]}',
            '{}',
            '{"builds":[{"result":"SUCCESS"},{"result":"FAILURE"}]}',
            '{"building":False,"result":"SUCCESS","timestamp":' + str(int(timestamp)) + '}']
        self.assertEqual([('jenkins/job1', 'http://jenkins/job/job1/', '100')], self.__jenkins.failing_jobs_url())

    def test_failing_jobs_url_no_description(self, mock_url_read):
        """ Test that the failing jobs url works if there are jobs without description. """
        now = datetime.datetime.utcnow()
        jan_first = now.replace(month=1, day=1, hour=0, minute=0, second=0)
        if now.month == now.day == 1:  # pragma: no branch
            jan_first = jan_first.replace(year=jan_first.year - 1)  # pragma: no cover
        mock_url_read.side_effect = [
            '{"jobs":[{"description":None,"name":"_","url":"http://jenkins/x/x/"}]}',
            '{"jobs":[{"name":"job1","url":"http://jenkins/job/job1/","buildable":True, "color":"red", '
            '"description": None}]}',
            '{}',
            '{"builds":[{"result":"SUCCESS"},{"result":"FAILURE"}]}',
            '{"building":False,"result":"SUCCESS","timestamp":' + str(int(to_jenkins_timestamp(jan_first))) + '}']
        expected_days_ago = (datetime.datetime.utcnow() - jan_first).days
        self.assertEqual([('jenkins/job1', 'http://jenkins/job/job1/', '{0:d}'.format(expected_days_ago))],
                         self.__jenkins.failing_jobs_url())

    def test_building_job_not_failing_jobs(self, mock_url_read):
        """ Test that the currently building jobs are not considered. """
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"proj-pipeline","url":"http://jenkins.proj/job/proj-pipeline/"}]}',
            '{"jobs":[{"description":None,"name":"_","url":"http://jenkins.proj/","buildable":True,"color":"red"}]}',
            '{}',
            '{"builds":[{"result":"SUCCESS", "building":True}]}']
        self.assertEqual(0, self.__jenkins.number_of_failing_jobs())

    def test_no_unused_jobs(self, mock_url_read):
        """ Test the number of unused jobs when there are no unused jobs. """
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            '{"jobs":[{"name":"job1","url":"http://jenkins/job/job1/","color":"red"}]}',
            '{}']
        self.assertEqual(0, self.__jenkins.number_of_unused_jobs())

    def test_no_unused_jobs_url(self, mock_url_read):
        """ Test the number of unused jobs when there are no unused jobs. """
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            '{"jobs":[{"name":"job1","url":"http://jenkins/job/job1/","color":"red"}]}',
            '{}']
        self.assertEqual([], self.__jenkins.unused_jobs_url())

    def test_failing_jobs_url_http_error(self, mock_url_read):
        """ Test the number of unused jobs when there are no unused jobs. """
        mock_url_read.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        self.assertEqual([], self.__jenkins.failing_jobs_url())

    def test_unused_jobs_url_http_error(self, mock_url_read):
        """ Test the number of unused jobs when there are no unused jobs. """
        mock_url_read.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        self.assertEqual([], self.__jenkins.unused_jobs_url())

    def test_one_unused_job(self, mock_url_read):
        """ Test the unused jobs with one unused job. """
        date_time = datetime.datetime(2000, 4, 1, 12, 0, 0)
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            '{"jobs":[{"name":"job1","description":"","url":"http://jenkins/job/job1/","buildable":True}]}',
            '{"builds":[{"result":"SUCCESS"}]}',
            '{"building":False,"result":"SUCCESS","timestamp":' + str(int(to_jenkins_timestamp(date_time))) + '}']
        self.assertEqual(1, self.__jenkins.number_of_unused_jobs())

    def test_one_unused_job_url(self, mock_url_read):
        """ Test the unused jobs with one unused job. """
        date_time = datetime.datetime(2000, 4, 1, 12, 0, 0)
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            '{"jobs":[{"name":"job1","description":"","url":"http://jenkins/job/job1/","buildable":True}]}',
            '{}',
            '{"builds":[{"result":"SUCCESS"}]}', '{"building":False,"result":"SUCCESS","timestamp":10000}',
            '{"building":"False","result":"SUCCESS","timestamp":' + str(int(to_jenkins_timestamp(date_time))) + '}']
        expected_days_ago = (datetime.datetime.utcnow() - date_time).days
        self.assertEqual([('jenkins/job1', 'http://jenkins/job/job1/', '{0:d}'.format(expected_days_ago))],
                         self.__jenkins.unused_jobs_url())

    def test_unused_jobs_grace(self, mock_url_read):
        """ Test the unused jobs with one unused job within grace time. """
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            '{"jobs":[{"name":"job1","description":"[gracedays=200]","url":"http://xx/job1/","buildable":True}]}',
            '{}',
            '{"builds":[{"result":"SUCCESS"},{"result":"FAILURE"}]}',
            '{"building":False,"result":"SUCCESS","timestamp":' + str(
                int(to_jenkins_timestamp(datetime.datetime.utcnow() - datetime.timedelta(days=100)))) + '}']

        self.assertEqual([], self.__jenkins.unused_jobs_url())

    def test_unused_jobs_after_grace(self, mock_url_read):
        """ Test the unused jobs with one unused job within grace time. """
        last_year = datetime.datetime.utcnow().year - 1
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            '{"jobs":[{"name":"job1","description":"[gracedays=200]","url":"http://xx/job1/","buildable":True}]}',
            '{}',
            '{"builds":[{"result":"SUCCESS"}]}',
            '{"building":False,"result":"SUCCESS","timestamp":' + str(
                int(to_jenkins_timestamp(datetime.datetime(last_year, 1, 1, 12, 0, 0)))) + '}',
            '{"building":False,"result":"SUCCESS","timestamp":' + str(
                int(to_jenkins_timestamp(datetime.datetime(last_year, 1, 1, 12, 0, 0)))) + '}']

        expected_days_ago = (datetime.datetime.utcnow() - datetime.datetime(last_year, 1, 1, 12, 0, 0)).days
        self.assertEqual([('job1', 'http://xx/job1/', '{0:d}'.format(expected_days_ago))],
                         self.__jenkins.unused_jobs_url())

    def test_nr_of_active_jobs(self, mock_url_read):
        """ Test the number of active jobs. """
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            '{"jobs":[{"name":"job1","url":"http://jenkins/job/job1/","color":"red"}]}',
            '{}']
        self.assertEqual(0, self.__jenkins.number_of_active_jobs())

    def test_nr_of_active_jobs_error_subjobs(self, mock_url_read):
        """ Test the number of active jobs. """
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            '{"invalid": "json"}']
        self.assertEqual(0, self.__jenkins.number_of_active_jobs())

    def test_nr_of_active_jobs_on_error(self, mock_url_read):
        """ Test that the number of active jobs is -1 when an URL error is thrown. """
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            urllib.error.URLError('some reason')]

        self.assertEqual(-1, self.__jenkins.number_of_active_jobs())

    def test_nr_of_failing_jobs_on_error(self, mock_url_read):
        """ Test that the number of failing jobs is -1 when an URL error is thrown. """
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            urllib.error.URLError('some reason')]
        self.assertEqual(-1, self.__jenkins.number_of_failing_jobs())

    def test_nr_of_unused_jobs_on_error(self, mock_url_read):
        """ Test that the number of unused jobs is -1 when an URL error is thrown. """
        mock_url_read.side_effect = [
            '{"jobs":[{"description":"","name":"_","url":"http://jenkins/x/x/"}]}',
            urllib.error.URLError('some reason')]
        self.assertEqual(-1, self.__jenkins.number_of_unused_jobs())
