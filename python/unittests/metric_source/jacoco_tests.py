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

import BeautifulSoup
import datetime
import unittest
import urllib2
from qualitylib.metric_source import JaCoCo


class JaCoCoUnderTest(JaCoCo):
    ''' Override the soup method to return a fixed HTML fragment. '''
    html = '<tfoot><tr><td>Total</td><td class="bar">1,162 of 6,293</td>' \
        '<td class="ctr2">82%</td><td class="bar">161 of 422</td>' \
        '<td class="ctr2">62%</td><td class="ctr1">287</td>' \
        '<td class="ctr2">807</td><td class="ctr1">297</td>' \
        '<td class="ctr2">1,577</td><td class="ctr1">138</td>' \
        '<td class="ctr2">592</td><td class="ctr1">12</td>' \
        '<td class="ctr2">79</td></tr></tfoot>'
    date_html = '<tbody><tr><td><span class="el_session">na-node1-reg-' \
        '1196e1b5</span></td><td>Apr 4, 2013 4:41:29 PM</td><td>Apr 5, 2013 ' \
        '10:34:54 AM</td></tr><tr><td><span class="el_session">na-node2-reg-' \
        '1f82fbab</span></td><td>Apr 4, 2013 4:43:39 PM</td><td>Apr 5, 2013 ' \
        '10:34:55 AM</td></tr></tbody>'

    def soup(self, url):
        if 'raise' in url:
            raise urllib2.HTTPError(url, None, None, None, None)
        else:
            html = self.html if url.endswith('index.html') else self.date_html
            return BeautifulSoup.BeautifulSoup(html)

    
class JacocoTest(unittest.TestCase):  
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the Jacoco class. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        self.__jacoco = JaCoCoUnderTest('http://jacoco/%s/index.html', 
                                        'username', 'password')
        
    def test_coverage(self):
        ''' Test the coverage for a specific product. '''
        self.assertEqual(round(100 * (6293 - 1162) / 6293.), 
                         self.__jacoco.coverage('product'))
        
    def test_zero_coverage(self):
        ''' Test zero coverage. '''
        self.__jacoco.html = '<tfoot><tr>' \
            '<td>Total</td><td class="bar">0 of 0</td>' \
            '<td class="ctr2">0%</td><td class="bar">0 of 0</td>' \
            '<td class="ctr2">0%</td><td class="ctr1">0</td>' \
            '<td class="ctr2">0</td><td class="ctr1">0</td>' \
            '<td class="ctr2">0</td><td class="ctr1">0</td>' \
            '<td class="ctr2">0</td><td class="ctr1">0</td>' \
            '<td class="ctr2">0</td></tr></tfoot>'
        self.assertEqual(0, self.__jacoco.coverage('product'))
        
    def test_coverage_on_error(self):
        ''' Test that the reported coverage is -1 when Jacoco can't be 
            reached. '''
        self.assertEqual(-1, self.__jacoco.coverage('raise'))
        
    def test_coverage_date(self):
        ''' Test the date of the coverage report. '''
        expected = datetime.datetime(2013, 4, 5, 10, 34, 55)
        self.assertEqual(expected, self.__jacoco.coverage_date('product'))

    def test_coverage_date_on_error(self):
        ''' Test that the date is now when JaCoCo can't be reached. '''
        coverage_date = self.__jacoco.coverage_date('raise')
        age = datetime.datetime.now() - coverage_date
        self.failUnless(age < datetime.timedelta(seconds=1))
        
    def test_coverage_date_url(self):
        ''' Test that the coverage date url is different than the coverage
            url for JaCoCo. '''
        self.assertEqual('http://jacoco/product/.sessions.html', 
                         self.__jacoco.get_coverage_date_url('product'))
        