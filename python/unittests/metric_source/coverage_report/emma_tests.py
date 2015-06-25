'''
Copyright 2012-2015 Ministerie van Sociale Zaken en Werkgelegenheid

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
from qualitylib.metric_source import Emma


class FakeJenkins(object):
    ''' Fake Jenkins to provide fixed data. '''
    html = '<th class="tl"><a>EMMA</a> Coverage Report (generated ' \
           'Tue Jan 29 15:02:28 CET 2013)</th>' \
           '<td></td><td></td><td></td><td></td><td></td><td>99%</td>'
    alternative_datetime_format_html = '<th class="tl"><a>EMMA</a> Coverage ' \
           'Report (generated Tue Okt 29 15:02:28 CET 2013)</th>' \
           '<td></td><td></td><td></td><td></td><td></td><td>99%</td>'

    @staticmethod
    def url():
        ''' Return the Jenkins url. '''
        return 'http://jenkins/'

    def url_open(self, url):
        ''' Open a url. '''
        if 'raise' in url:
            raise urllib2.HTTPError(url, None, None, None, None)
        else:
            return self.html

    @staticmethod
    def resolve_job_name(job_re):
        ''' Resolve the job regular expression to a concrete job name. '''
        return job_re


class EmmaTest(unittest.TestCase):  
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the Emma class. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__jenkins = FakeJenkins()
        self.__emma = Emma(self.__jenkins, '{}/')

    def test_coverage(self):
        ''' Test the coverage for a specific product. '''
        self.assertEqual(99, self.__emma.coverage('product'))

    def test_coverage_on_error(self):
        ''' Test that the reported coverage is -1 when Emma can't be 
            reached. '''
        self.assertEqual(-1, self.__emma.coverage('raise'))

    def test_coverage_date(self):
        ''' Test the date of the coverage report. '''
        self.assertEqual(datetime.datetime(2013, 1, 29, 15, 2, 28), 
                         self.__emma.coverage_date('product'))

    def test_coverage_date_alt_format(self):
        ''' Test the date of the coverage report without timezone. '''
        self.__jenkins.html = self.__jenkins.alternative_datetime_format_html
        self.assertEqual(datetime.datetime(2013, 10, 29, 15, 2, 28), 
                         self.__emma.coverage_date('product'))

    def test_coverage_date_on_error(self):
        ''' Test that the date is now when Emma can't be reached. '''
        coverage_date = self.__emma.coverage_date('raise')
        age = datetime.datetime.now() - coverage_date
        self.assertTrue(age < datetime.timedelta(seconds=1))
