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
import urllib.error

from hqlib.metric_source import SilkPerformerPerformanceLoadTestReport


HTML = r"""
<html>
    <head>
    <title>ABC Performancetest Summary [2016.04.19.02.44.48]</title>
    </head>
    <body>

<table width="100%"><tr>
<td>
    <h1>ABC Performancetest Summary [2016.04.19.02.44.48]</h1>
    </td>
<td align="right">
Reporting engine
</td></tr></table>

<hr align="left" width="100%" size="1"/>

<p class="Failure"></p>

<table><tr valign="top"><td>

<h3>Test specification</h3>
<table class="config">
    <tr><td class="name">Comment</td><td>Gegenereerd vanuit de TestStraat</td></tr>
    <tr><td class="name">Workload</td><td>Productie</td></tr>
    <tr><td class="name">Report generated</td><td>2016.04.19.03.27.56</td></tr>
    <tr><td class="name">Start of the test (GMT)</td><td>2016.04.19.02.44.48</td></tr>
    <tr><td class="name">Baseline</td><td>2016.04.18.13.47.02</td></tr>
    <tr><td class="name">Number of virtual users</td><td>12</td></tr>
</table>

<h3>Components</h3>
<table class="config">
    <tr><td class="name">ABC frontend servers (st)</td><td>host60.abc.com/host61.abc.com</td></tr>
    <tr><td class="name">ABC backend servers (st)</td><td>host65.abc.com/host66.abc.com</td></tr>
    <tr><td class="name">ABC database servers (st)</td><td>host70.abc.com</td></tr>
    <tr><td class="name">ABC application appversion</td><td>8.1.1.57</td--></tr>
    <tr><td class="name">ABC database appversion</td><td>6.1.4-4002</td></tr>
    <tr><td class="name">Performancetest scripts SVN tag</td><td>3.2</td></tr>
</table>

</td><td>

<h3></h3>
<table class="config">
    <tr><td class="name">'No data' value</td><td></td></tr>
    <tr><td class="name">(st)</td><td>static data, not dynamically retrieved</td></tr>
    <tr><td class="name">Evaluated</td><td>Requirements are evaluated against this value</td></tr>
    <tr><td class="name">Baseline</td><td>Baseline reference evaluated value</td></tr>
    <tr><td class="name">Current</td><td>This measurement's evaluated value, to be compared with baseline</td></tr>
    <tr><td class="name">Delta %</td><td>Comparison of evaluated values between current and baseline,
    relative to the baseline<br>
    Color codes for delta field:<br>
    red indicates substantial increase of responsetimes (delta > 15%)<br>
    green indicates substantial reduction of responsetimes (delta < -15%)</td></tr>
</table>

</td><td>

<h3>Thresholds</h3>
<table class="config">
    <tr><td></td><td class="header">OK</td><td class="header">WARNING</td><td class="header">HIGH</tr>
    <tr><td class="name">generic</td><td class="green"></td><td class="yellow">1</td><td class="red">1</td></tr>
</table>

</td>
</tr></table>

<hr align="left" width="100%" size="1"/>
    <h2>Responsetimes (ms)</h2>

<table width="100%" cellspacing="2" cellpadding="5" border="0" class="details">
    <tr valign="top">
    <th class="blank"/><th class="blank"/><th class="blank"/><th class="blank"/><th class="blank"/><th class="blank">
    Evaluated</th><th class="blank"/><th class="blank"/><th class="blank"/><th class="blank"/><th class="blank"/>
    <th class="blank">Baseline</th><th class="blank">Current</th><th class="blank"/>
    </tr>
    <tr valign="top">
    <th>Id</th><th>Transaction</th><th>Success</th><th>Min</th><th>Avg</th><th>90 perc</th><th>Max</th><th>StDev</th>
    <th>Failed</th><th>Canceled</th><th class="blank"></th><th>v7.2.0.46</br>2016.04.18.13.47.02</th>
    <th>v7.2.0.46</br>2016.04.19.02.44.48</th><th>Delta %</th>
    </tr>
    <tr valign="top" class="">
    <td>1</td><td class="name">01</td>
    <td>78</td>
    <td class="green">0.048</td>
    <td class="green">0.089</td>
    <td class="green">0.198</td>
    <td class="green">0.219</td>
    <td>0.038</td><td></td><td></td>
    <td class="blank"/>
    <td>0.102</td><td>0.198</td><td class=""></td>
    </tr>
    <tr valign="top" class="">
    <td>2</td><td class="name">02</td>
    <td>77</td>
    <td class="green">0.180</td>
    <td class="green">0.330</td>
    <td class="green">0.444</td>
    <td class="green">0.686</td>
    <td>0.077</td><td></td><td></td>
    <td class="blank"/>
    <td>0.410</td><td>0.444</td><td class=""></td>
    </tr>
    <tr valign="top" class="">
    <td>3</td><td class="name">03</td>
    <td>76</td>
    <td class="green">0.253</td>
    <td class="green">0.376</td>
    <td class="green">0.476</td>
    <td class="green">0.569</td>
    <td>0.046</td><td></td><td></td>
    <td class="blank"/>
    <td>0.605</td><td>0.476</td><td class=""></td>
    </tr>
    <tr valign="top" class="">
    <td>4</td><td class="name">04</td>
    <td>76</td>
    <td class="green">0.046</td>
    <td class="green">0.078</td>
    <td class="green">0.102</td>
    <td class="green">0.502</td>
    <td>0.054</td><td></td><td></td>
    <td class="blank"/>
    <td>0.100</td><td>0.102</td><td class=""></td>
    </tr>
    <tr valign="top" class="">
    <td>5</td><td class="name">05</td>
    <td>75</td>
    <td class="green">0.104</td>
    <td class="green">0.187</td>
    <td class="green">0.292</td>
    <td class="green">0.434</td>
    <td>0.059</td><td></td><td></td>
    <td class="blank"/>
    <td>0.249</td><td>0.292</td><td class=""></td>
    </tr>
    <tr valign="top" class="">

    <tr valign="top">
    <th>Id</th><th>Transaction</th><th>Success</th><th>Min</th><th>Avg</th><th>90 perc</th><th>Max</th><th>StDev</th>
    <th>Failed</th><th>Canceled</th><th class="blank"></th><th>v7.2.0.46</br>2016.04.18.13.47.02</th>
    <th>v7.2.0.46</br>2016.04.19.02.44.48</th><th>Delta %</th>
    </tr>
    <tr valign="top" class="">
    <td>6</td><td class="name">03</td>
    <td>31</td>
    <td class="green">0.282</td>
    <td class="green">0.510</td>
    <td class="green">0.636</td>
    <td class="red">1.098</td>
    <td>0.200</td><td></td><td></td>
    <td class="blank"/>
    <td>0.696</td><td>0.636</td><td class=""></td>
    </tr>
    <tr valign="top" class="">
    <td>7</td><td class="name">04</td>
    <td>31</td>
    <td class="green">0.123</td>
    <td class="green">0.176</td>
    <td class="green">0.237</td>
    <td class="green">0.237</td>
    <td>0.044</td><td></td><td></td>
    <td class="blank"/>
    <td>0.252</td><td>0.237</td><td class=""></td>
    </tr>
    <tr valign="top" class="">
    <td>8</td><td class="name">05</td>
    <td>30</td>
    <td class="green">0.040</td>
    <td class="green">0.064</td>
    <td class="green">0.081</td>
    <td class="green">0.083</td>
    <td>0.009</td><td></td><td></td>
    <td class="blank"/>
    <td>0.091</td><td>0.081</td><td class=""></td>
    </tr>
    <tr valign="top" class="">
    <td>9</td><td class="name">06</td>
    <td>30</td>
    <td class="green">0.056</td>
    <td class="green">0.086</td>
    <td class="green">0.114</td>
    <td class="green">0.129</td>
    <td>0.024</td><td></td><td></td>
    <td class="blank"/>
    <td>0.181</td><td>0.114</td><td class=""></td>
    </tr>

    <tr valign="top">
    <th>Id</th><th>Transaction</th><th>Success</th><th>Min</th><th>Avg</th><th>90 perc</th><th>Max</th><th>StDev</th>
    <th>Failed</th><th>Canceled</th><th class="blank"></th><th>v7.2.0.46</br>2016.04.18.13.47.02</th>
    <th>v7.2.0.46</br>2016.04.19.02.44.48</th><th>Delta %</th>
    </tr>

    <tr valign="top" class="">
    <td>10</td><td class="name">01</td>
    <td>83</td>
    <td class="green">0.049</td>
    <td class="green">0.085</td>
    <td class="green">0.107</td>
    <td class="green">0.216</td>
    <td>0.030</td><td></td><td></td>
    <td class="blank"/>
    <td>0.094</td><td>0.107</td><td class=""></td>
    </tr>
    <tr valign="top" class="">
    <td>11</td><td class="name">02</td>
    <td>83</td>
    <td class="green">0.300</td>
    <td class="green">0.537</td>
    <td class="green">0.630</td>
    <td class="green">0.853</td>
    <td>0.099</td><td></td><td></td>
    <td class="blank"/>
    <td>0.655</td><td>0.630</td><td class=""></td>
    </tr>
    <tr valign="top" class="">
    <td>12</td><td class="name">03</td>
    <td>82</td>
    <td class="green">0.200</td>
    <td class="green">0.368</td>
    <td class="green">0.458</td>
    <td class="green">0.724</td>
    <td>0.092</td><td></td><td></td>
    <td class="blank"/>
    <td>0.537</td><td>0.458</td><td class=""></td>
    </tr>
    <tr valign="top" class="">
    <td>13</td><td class="name">04</td>
    <td>82</td>
    <td class="green">0.044</td>
    <td class="green">0.109</td>
    <td class="green">0.208</td>
    <td class="green">0.319</td>
    <td>0.073</td><td></td><td></td>
    <td class="blank"/>
    <td>0.206</td><td>0.208</td><td class=""></td>
    </tr>
    <tr valign="top" class="">
    <td>14</td><td class="name">05</td>
    <td>81</td>
    <td class="green">0.043</td>
    <td class="green">0.113</td>
    <td class="green">0.265</td>
    <td class="green">0.674</td>
    <td>0.091</td><td></td><td></td>
    <td class="blank"/>
    <td>0.204</td><td>0.265</td><td class=""></td>
    </tr>
    <tr valign="top" class="">
    <td>15</td><td class="name">06</td>
    <td>79</td>
    <td class="green">0.291</td>
    <td class="green">0.481</td>
    <td class="green">0.636</td>
    <td class="green">0.992</td>
    <td>0.161</td><td></td><td></td>
    <td class="blank"/>
    <td>0.710</td><td>0.636</td><td class=""></td>
    </tr>
    <tr valign="top" class="">
    <td>16</td><td class="name">07</td>
    <td>79</td>
    <td class="green">0.027</td>
    <td class="green">0.109</td>
    <td class="green">0.058</td>
    <td class="green">0.618</td>
    <td>0.160</td><td></td><td></td>
    <td class="blank"/>
    <td>0.301</td><td>0.058</td><td class=""></td>
    </tr>
    <tr valign="top" class="">
    <td>17</td><td class="name">09</td>
    <td>78</td>
    <td class="green">0.095</td>
    <td class="green">0.175</td>
    <td class="green">0.228</td>
    <td class="green">0.560</td>
    <td>0.066</td><td></td><td></td>
    <td class="blank"/>
    <td>0.213</td><td>0.228</td><td class=""></td>
    </tr>
</table>

</body></html>
"""


class SilkPerformerUnderTest(SilkPerformerPerformanceLoadTestReport):  # pylint: disable=too-few-public-methods
    """ Override the Silk Performer performance report to return the url as report contents. """

    def url_open(self, url):  # pylint: disable=no-self-use
        """ Return the static html. """
        if 'error' in url:
            raise urllib.error.URLError('reason')
        else:
            return HTML


class SilkPerformerTest(unittest.TestCase):
    """ Unit tests for the Silk Performer performance report metric source. """
    expected_queries = 17

    def setUp(self):
        SilkPerformerUnderTest.queries.cache_clear()
        self._performance_report = SilkPerformerUnderTest('http://report/')

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual('http://report/', self._performance_report.url())

    def test_queries_non_existing(self):
        """ Test that the number of queries for a product/version that is not found is zero. """
        self.assertEqual(0, self._performance_report.queries('product'))

    def test_queries(self):
        """ Test that the total number of queries for a product/version that is in the report. """
        self.assertEqual(self.expected_queries, self._performance_report.queries(('.*[0-9][0-9].*', 'dummy')))

    def test_queries_violating_max_responsetime(self):
        """ Test that the number of queries violating the maximum response times is zero. """
        self.assertEqual(0, self._performance_report.queries_violating_max_responsetime(('.*[0-9][0-9].*', 'dummy')))

    def test_queries_violating_wished_reponsetime(self):
        """ Test that the number of queries violating the wished response times is zero. """
        self.assertEqual(0, self._performance_report.queries_violating_wished_responsetime(('.*[0-9][0-9].*', 'dummy')))

    def test_date_of_last_measurement(self):
        """ Test that the date of the last measurement is correctly parsed from the report. """
        self.assertEqual(datetime.datetime(2016, 4, 19, 3, 27, 56),
                         self._performance_report.datetime(('.*[0-9][0-9].*', 'dummy')))

    def test_date_without_urls(self):
        """ Test that the min date is passed if there are no report urls to consult. """
        class SilkPerformerWithoutUrls(SilkPerformerUnderTest):
            """ Simulate missing urls. """
            def urls(self, product):  # pylint: disable=unused-argument
                return []

        self.assertEqual(datetime.datetime.min,
                         SilkPerformerWithoutUrls('http://report').datetime(('.*[0-9][0-9].*', 'dummy')))


class SilkPerformerMultipleReportsTest(SilkPerformerTest):
    """ Unit tests for the Silk Performer performance report metric source with multiple reports. """

    expected_queries = 2 * SilkPerformerTest.expected_queries

    def setUp(self):
        self._performance_report = SilkPerformerUnderTest('http://report/',
                                                          report_urls=['http://report/1', 'http://report/2'])


class SilkPerformerMissingTest(unittest.TestCase):
    """ Unit tests for a missing Silk Performer performance report metric source. """

    def test_queries_with_missing_report(self):
        """ Test that the value of a missing report is -1. """
        self.assertEqual(-1, SilkPerformerUnderTest('http://error/').queries('p1'))

    def test_queries_max_responsetime_with_missing_report(self):
        """ Test that the value of a missing report is -1. """
        self.assertEqual(-1, SilkPerformerUnderTest('http://error/').queries_violating_max_responsetime('p2'))

    def test_queries_wished_reponsetime_with_missing_report(self):
        """ Test that the value of a missing report is -1. """
        self.assertEqual(-1, SilkPerformerUnderTest('http://error/').queries_violating_wished_responsetime('p3'))

    def test_date_with_missing_report(self):
        """ Test that the date of a missing report is the min date. """
        self.assertEqual(datetime.datetime.min, SilkPerformerUnderTest('http://error/').datetime('p4'))
