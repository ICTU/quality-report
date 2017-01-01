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

import datetime
import unittest
import bs4

from hqlib.metric_source import JMeterPerformanceLoadTestReport

HTML = """
<table>
  <caption>Applicaties op n-das-pp-perf.lrk.org</caption>
  <tbody>
    <tr>
      <td>lrk-pp-ear-12.5.5</td>
    </tr>
    <tr>
      <td>kotb-dblogger-ear-0.4.13</td>
    </tr>
  </tbody>
</table>
<table>
  <caption>Applicaties op n-das-perf.lrk.org</caption>
  <tbody>
    <tr>
      <td>gir-inspecteren-ear-8.5.1</td>
    </tr>
    <tr>
      <td>gir-handhaven-ear-8.3.2</td>
    </tr>
  </tbody>
</table>
<h2>Response times (ms): stable period - Begin: Fri Aug 28 13:40:30 CEST 2015 - End: Fri Aug 28 15:41:30 CEST 2015</h2>
<table class="details">
  <tr>
    <th>Id</th>
    <th>UI transaction</th>
    <th>Count</th>
    <th>Sum</th>
    <th>First</th>
    <th>Last</th>
    <th>Min</th>
    <th>Avg</th>
    <th>Median</th>
    <th>80 perc</th>
    <th>90 perc</th>
    <th>Max</th>
    <th>StDev</th>
    <th>Error %</th>
    <th>Min req</th>
    <th>Max req</th>
    <th>Min %</th>
    <th>Max %</th>
    <th>Errors</th>
    <th>Startup?</th>
  </tr>
  <tr class="">
    <td>1</td>
    <td class="name">01000_hoofdpagina_pp</td>
    <td>119</td>
    <td>3.971</td>
    <td>24</td>
    <td>21</td>
    <td class="green">20</td>
    <td class="green">33</td>
    <td class="green">28</td>
    <td class="green">29</td>
    <td class="red">800</td>
    <td class="green">881</td>
    <td>78</td>
    <td class="green">0</td>
    <td>1.000</td>
    <td>4.000</td>
    <td class="green">100</td>
    <td class="green">100</td>
    <td class="green">0</td>
    <td>N</td>
  </tr>
    <tr class="">
    <td>2</td>
    <td class="name">01010_linkzoekscherm</td>
    <td>119</td>
    <td>4.704</td>
    <td>41</td>
    <td>39</td>
    <td class="green">31</td>
    <td class="green">39</td>
    <td class="green">38</td>
    <td class="green">39</td>
    <td class="green">46</td>
    <td class="green">82</td>
    <td>11</td>
    <td class="green">0</td>
    <td>1.000</td>
    <td>4.000</td>
    <td class="green">100</td>
    <td class="green">100</td>
    <td class="green">0</td>
    <td>N</td>
  </tr>
</table>"""


class JMeterUnderTest(JMeterPerformanceLoadTestReport):
    """ Override the JMeter performance report to return the url as report contents. """
    # pylint: disable=unused-argument,no-self-use

    def url_open(self, url):
        """ Return the static HTML. """
        return HTML

    def soup(self, url):
        return bs4.BeautifulSoup('<li><a>1.html</a></li>', "html.parser") if url == self.url() \
            else super(JMeterUnderTest, self).soup(url)


class JMeterTest(unittest.TestCase):
    """ Unit tests for the JMeter performance report metric source. """

    def setUp(self):
        self.__performance_report = JMeterUnderTest('http://report/')

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual('http://report/', self.__performance_report.url())

    def test_queries_non_existing(self):
        """ Test that the number of queries for a product/version that is not found is zero. """
        self.assertEqual(0, self.__performance_report.queries('product'))

    def test_queries(self):
        """ Test that the total number of queries for a product/version that is in the report. """
        self.assertEqual(2, self.__performance_report.queries(('01', 'lrk-pp')))

    def test_queries_violating_max_responsetime(self):
        """ Test that the number of queries violating the maximum response times is zero. """
        self.assertEqual(1, self.__performance_report.queries_violating_max_responsetime(('01', 'lrk-pp')))

    def test_queries_violating_wished_reponsetime(self):
        """ Test that the number of queries violating the wished response times is zero. """
        self.assertEqual(0, self.__performance_report.queries_violating_wished_responsetime(('01', 'lrk-pp')))

    def test_date_of_last_measurement(self):
        """ Test that the date of the last measurement is correctly parsed from the report. """
        self.assertEqual(datetime.datetime(2015, 8, 28, 15, 41, 30),
                         self.__performance_report.date(('01', 'lrk-pp')))

    def test_date_product_not_found(self):
        """ Test the date when the product/version is not in the report. """
        self.assertEqual(datetime.datetime(2015, 8, 28, 15, 41, 30), self.__performance_report.date('product'))

    def test_urls(self):
        """ Test the urls. """
        self.assertEqual({u'http://report/1.html'}, self.__performance_report.urls(('01', 'lrk-pp')))
