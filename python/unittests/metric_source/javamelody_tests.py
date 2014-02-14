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

from qualitylib.metric_source import JavaMelody
import BeautifulSoup
import datetime
import unittest


HTTP_DETAILS_HTML = '''
    <div id='detailshttp'>
      <table>
        <thead>
          <tr>
            <th>Request</th>
            <th>% of cumulative time</th>
            <th>Hits</th>
            <th>Mean time (ms)</th>
            <th>Max time (ms)</th>
            <th>Standard deviation</th>
            <th>% of cumulative cpu time</th>
            <th>Mean cpu time (ms)</th>
            <th>% of system error</th>
            <th>Mean size (Kb)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><a><em><img/></em>/gddbaZoekService POST</a></td>
            <td>82</td>
            <td>80</td>
            <td><span>20.317</span></td> 
            <td>20.506</td> 
            <td>136</td>
            <td>39</td>
            <td><span>41</span></td>
            <td>0,00</td>
            <td>6</td>
          </tr>
          <tr>
            <td><a><em><img/></em>/gddbaDossierService POST</a></td>
            <td>17</td>
            <td>133</td>
            <td><span>2.589</span></td>
            <td>15.252</td>
            <td>3.482</td>
            <td>60</td><td><span>38</span></td>
            <td>0,00</td>
            <td>4</td>
          </tr>
        </tbody>
      </table>
    </div>'''


EJB_DETAILS_HTML = '''
    <div id='detailsejb'>
      <table>
        <thead>
          <tr>
            <th>Request</th>
            <th>% of cumulative time</th>
            <th>Hits</th>
            <th>Mean time (ms)</th>
            <th>Max time (ms)</th>
            <th>Standard deviation</th>
            <th>% of cumulative cpu time</th>
            <th>Mean cpu time (ms)</th>
            <th>% of system error</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td></td>
            <td>73</td>
            <td>241</td>
            <td><span class='info'>770</span></td>
            <td>1.981</td>
            <td>475</td>
            <td>41</td>
            <td><span class='info'>20</span></td>
            <td>0,00</td>
          </tr>
          <tr>
            <td></td>
            <td>26</td>
            <td>222</td>
            <td><span class='info'>306</span></td>
            <td>3.361</td>
            <td>706</td>
            <td>58</td>
            <td><span class='info'>31</span></td>
            <td>0,00</td>
          </tr>
        </tbody>
      </table>
    </div>'''
    

class JavaMelodyUnderTest(JavaMelody):
    ''' Override the soup method to return a fixed HTML fragment. '''
    html = ''
    def soup(self, url):
        return BeautifulSoup.BeautifulSoup(self.html)
    

class JavaMelodyTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the JavaMelody class. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        self.__javamelody = JavaMelodyUnderTest('http://javamelody')
        self.__start = datetime.date(2013, 1, 1)
        self.__end = datetime.date(2013, 1, 31)
        
    def test_url_without_product(self):
        ''' Test that the url is correct. '''
        self.assertEqual('http://javamelody', self.__javamelody.url())
        
    def test_url_with_product(self):
        ''' Test that the url is correct. '''
        self.assertEqual('http://javamelody?application=product_id&'
                         'startDate=1-1-13&endDate=31-1-13'
                         '&period=1-1-13%7C31-1-13', 
                         self.__javamelody.url('product_id',  
                                               self.__start, self.__end))
        
    def test_mean_request_times_http(self):
        ''' Test that JavaMelody returns a list of mean request times. '''
        self.__javamelody.html = HTTP_DETAILS_HTML
        self.assertEqual([20317, 2589], 
                         self.__javamelody.mean_request_times('product_id',
                                                              self.__start,
                                                              self.__end))
        
    def test_mean_request_times_ejb(self):
        ''' Test that JavaMelody returns a list of mean request times. '''
        self.__javamelody.html = EJB_DETAILS_HTML
        self.assertEqual([770, 306], 
                         self.__javamelody.mean_request_times('product_id',
                                                             self.__start, 
                                                             self.__end))
        
    def test_no_mean_request_times(self):
        ''' Test that JavaMelody returns an empty list of mean request 
            times. '''
        self.assertEqual([], 
                         self.__javamelody.mean_request_times('product_id',
                                                              self.__start, 
                                                              self.__end))
