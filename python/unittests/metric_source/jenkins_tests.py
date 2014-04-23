'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import datetime
import unittest
import urllib2
import StringIO
from qualitylib.metric_source import Jenkins
from qualitylib.domain import Team


class JenkinsUnderTest(Jenkins):
    ''' Override the url_open method to return a fixed HTML fragment. '''
    contents = '{"jobs": []}'

    def url_open(self, url):
        contents = self.contents
        if 'httperror' in self.contents:
            self.contents = 'raise'
        elif 'raise' in self.contents:
            raise urllib2.HTTPError(url, None, None, None, None)
        return StringIO.StringIO(contents)


class JenkinsTest(unittest.TestCase):  
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the Jenkins class. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__jenkins = JenkinsUnderTest('http://jenkins/', 'username', 
                                        'password')

    def test_url(self):
        ''' Test the Jenkins url. '''
        self.assertEqual('http://jenkins/', self.__jenkins.url())

    def test_no_failing_jobs(self):
        ''' Test the number of failing jobs when there are no failing jobs. '''
        self.assertEqual({}, self.__jenkins.failing_jobs_url())

    def test_one_failing_job(self):
        ''' Test the failing jobs with one failing job. '''
        self.__jenkins.contents = '{"jobs": [{"name": "job1", "color": "red", '\
            '"description": "", "url": "http://url", "buildable": True, ' \
            '"fakebuilddate": "<h1>(1-apr-2013 12:00:00)</h1>"}]}'
        expected_days_ago = (datetime.datetime.now() -  \
                             datetime.datetime(2013, 4, 1, 12, 0, 0)).days
        self.assertEqual({'job1 (%d dagen)' % expected_days_ago: 'http://url'}, 
                         self.__jenkins.failing_jobs_url())

    def test_ignore_disable_job(self):
        ''' Test that disabled failing jobs are ignored. '''
        self.__jenkins.contents = '{"jobs": [{"name": "job1", "color": "red", '\
            '"description": "", "url": "http://url", "buildable": False, ' \
            '"fakebuilddate": "<h1>(1-apr-2013 12:00:00)</h1>"}]}'
        self.assertEqual({}, self.__jenkins.failing_jobs_url())

    def test_failing_jobs_grace(self):
        ''' Test the failing jobs with one failing job within grace time. '''
        this_year = datetime.datetime.now().year
        self.__jenkins.contents = '{"jobs": [{"name": "job1", "color": "red", '\
            '"description": "[gracedays=400]", "url": "http://url", ' \
            '"fakebuilddate": "<h1>(1-jan-%d 12:00:00)</h1>", ' \
            '"buildable": True}]}' % this_year
        self.assertEqual({}, self.__jenkins.failing_jobs_url())

    def test_failing_jobs_after_grace(self):
        ''' Test the failing jobs with one failing job within grace time. '''
        last_year = datetime.datetime.now().year - 1
        self.__jenkins.contents = '{"jobs": [{"name": "job1", "color": "red", '\
            '"description": "[gracedays=200]", "url": "http://url", ' \
            '"fakebuilddate": "<h1>(1-jan-%d 12:00:00)</h1>", ' \
            '"buildable": True}]}' % last_year
        expected_days_ago = (datetime.datetime.now() - \
                             datetime.datetime(last_year, 1, 1, 12, 0, 0)).days
        self.assertEqual({'job1 (%d dagen)' % expected_days_ago: 'http://url'},
                         self.__jenkins.failing_jobs_url())

    def test_failing_jobs_by_team(self):
        ''' Test the failing jobs for a specific team. '''
        self.assertEqual({}, self.__jenkins.failing_jobs_url(Team('team 1')))

    def test_failing_jobs_url(self):
        ''' Test that the failing jobs url dictionary contains the url for the
            failing job. '''
        last_year = datetime.datetime.now().year
        self.__jenkins.contents = '{"jobs": [{"name": "job1", "color": "red", '\
            '"description": "", "url": "http://url", ' \
            '"fakebuilddate": "<h1>(1-jan-%d 12:00:00)</h1>", ' \
            '"buildable": True}]}' % last_year
        expected_days_ago = (datetime.datetime.now() - \
                             datetime.datetime(last_year, 1, 1, 12, 0, 0)).days
        self.assertEqual({'job1 (%d dagen)' % expected_days_ago: 'http://url'},
                         self.__jenkins.failing_jobs_url())

    def test_failing_jobs_url_no_description(self):
        ''' Test that the failing jobs url works if there are jobs without
            description. '''
        last_year = datetime.datetime.now().year
        self.__jenkins.contents = '{"jobs": [{"name": "job1", "color": "red", '\
            '"description": None, "url": "http://url", ' \
            '"fakebuilddate": "<h1>(1-jan-%d 12:00:00)</h1>", ' \
            '"buildable":  True}]}' % last_year
        expected_days_ago = (datetime.datetime.now() - \
                             datetime.datetime(last_year, 1, 1, 12, 0, 0)).days
        self.assertEqual({'job1 (%d dagen)' % expected_days_ago: 'http://url'},
                         self.__jenkins.failing_jobs_url())

    def test_no_unused_jobs(self):
        ''' Test the number of unused jobs when there are no unused jobs. '''
        self.assertEqual({}, self.__jenkins.unused_jobs_url())

    def test_one_unused_job(self):
        ''' Test the unused jobs with one unused job. '''
        self.__jenkins.contents = '{"jobs": [{"name": "job1", "color": "red", '\
            '"description": "", "url": "http://url", "buildable": True, ' \
            '"fakebuilddate": "<h1>(1-apr-2000 12:00:00)</h1>"}]}'
        expected_days_ago = (datetime.datetime.now() -  \
                             datetime.datetime(2000, 4, 1, 12, 0, 0)).days
        self.assertEqual({'job1 (%d dagen)' % expected_days_ago: 'http://url'}, 
                         self.__jenkins.unused_jobs_url())

    def test_nr_of_assigned_jobs(self):
        ''' Test the number of assigned jobs. '''
        self.assertEqual(0, self.__jenkins.number_of_assigned_jobs())

    def test_unassigned_jobs_url(self):
        ''' Test that the unassigned jobs url dictionary contains the url for
            the unassigned job. '''
        self.__jenkins.contents = '{"jobs": [{"name": "job1", '\
            '"description": "", "url": "http://url"}]}'
        self.assertEqual(dict(job1='http://url'), 
                         self.__jenkins.unassigned_jobs_url())

    def test_nr_of_jobs(self):
        ''' Test the number of jobs. '''
        self.assertEqual(0, self.__jenkins.number_of_jobs())

    def test_nr_of_jobs_for_team(self):
        ''' Test the number of jobs for a specific team. '''
        self.assertEqual(0, self.__jenkins.number_of_jobs(Team('team 1')))

    def test_unstable_arts_none(self):
        ''' Test the number of unstable ARTs. '''
        self.__jenkins.contents = '<table id="projectstatus"></table>'
        self.assertEqual({}, self.__jenkins.unstable_arts_url('projects', 21))

    def test_unstable_arts_one_just(self):
        ''' Test the number of unstable ARTs with one that just became 
            unstable. '''
        hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
        self.__jenkins.contents = '<table id="projectstatus"><a>job-a</a>' \
            '</table><h1>(%s)</h1>' % hour_ago.strftime('%d-%b-%Y %H:%M:%S')
        self.assertEqual({}, self.__jenkins.unstable_arts_url('job-a', 3))

    def test_unstable_arts_one(self):
        ''' Test the number of unstable ARTs. '''
        week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        self.__jenkins.contents = '<table id="projectstatus"><a>job-a</a>' \
            '</table><h1>(%s 0:00:00)</h1>' % week_ago.strftime('%d-%b-%Y')
        self.assertEqual({'job-a (7 dagen)': 'http://jenkins/job/job-a/'}, 
                         self.__jenkins.unstable_arts_url('job-a', 3))

    def test_unstable_art_old_age(self):
        ''' Test the unstable ART url for a build with a very old age. '''
        self.__jenkins.contents = '<table id="projectstatus"><a>job-a</a>' \
            '</table><h1>(1-jan-2000 0:00:00)</h1>'
        expected_days = (datetime.datetime.now() - \
                         datetime.datetime(2000, 1, 1, 0, 0, 0)).days
        self.assertEqual({'job-a (%s dagen)' % expected_days: 
                          'http://jenkins/job/job-a/'}, 
                         self.__jenkins.unstable_arts_url('job-a', 3))

    def test_unstable_art_dutch(self):
        ''' Test the unstable ART url for a build with a Dutch date. '''
        self.__jenkins.contents = '<table id="projectstatus"><a>job-a</a>' \
            '</table><h1>(1-mei-2000 0:00:00)</h1>'
        expected_days = (datetime.datetime.now() - \
                         datetime.datetime(2000, 5, 1, 0, 0, 0)).days
        self.assertEqual({'job-a (%s dagen)' % expected_days: 
                          'http://jenkins/job/job-a/'}, 
                         self.__jenkins.unstable_arts_url('job-a', 3))

    def test_unstable_art_parse_error(self):
        ''' Test the unstable ART url with a parse error occurring. '''
        self.__jenkins.contents = '<table id="projectstatus"><a>job-a</a>' \
            '</table><h1>(1-ABC-1 0:00:00)</h1>'
        self.assertRaises(KeyError, self.__jenkins.unstable_arts_url, 'job-a',
                          3)

    def test_unstable_art_http_error(self):
        ''' Test the unstable ART url with a HTTP error occurring. '''
        self.__jenkins.contents = '<table id="projectstatus"><a>job-a</a>' \
            '</table><h1>(1-jan-1 0:00:00)</h1>httperror'
        self.assertEqual({'job-a (? dagen)': 'http://jenkins/job/job-a/'},
                         self.__jenkins.unstable_arts_url('job-a', 3))
