"""
Copyright 2012-2016 Ministerie van Sociale Zaken en Werkgelegenheid

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

from qualitylib.metric_source import Ymor

HTML = r"""
<html>
    <head>
    <title>CS Performancetest Summary [2016.04.19.02.44.48]</title>
    </head>
    <body>

<table width="100%"><tr>
<td>
    <h1>CS Performancetest Summary [2016.04.19.02.44.48]</h1>
    </td>
<td align="right">
<img src="js\graph\logo_ymor_bt.png" height="15p"/>Reporting engine
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
    <tr><td class="name">CS frontend servers (st)</td><td>web160.cs.isd.local/web161.cs.isd.local</td></tr>
    <tr><td class="name">CS backend servers (st)</td><td>web165.cs.isd.local/web166.cs.isd.local</td></tr>
    <tr><td class="name">CS database servers (st)</td><td>sql170.cs.isd.local</td></tr>
    <tr><td class="name">CS application appversion</td><td>7.2.0.46</td--></tr>
    <tr><td class="name">CS database appversion</td><td>6.1.3-40302</td></tr>
    <tr><td class="name">Performancetest scripts SVN tag</td><td>3.6</td></tr>
</table>

</td><td>

<h3>Legend</h3>
<table class="config">
    <tr><td/><td class="header">functiongroup</td><td class="header">usecase</td></tr>
    <tr><td class="name">Ingeschrevenen</td><td>Werknemers</td><td>Inschrijven van persoon met bsn</td></tr>
    <tr><td class="name">Houder</td><td>Houders</td><td>Koppelen van persoon als werknemer</td></tr>
    <tr><td class="name">Beheerder</td><td>GGD Beheerders</td><td>Beheer van houders en personen</td></tr>
</table>

<h3></h3>
<table class="config">
    <tr><td class="name">'No data' value</td><td></td></tr>
    <tr><td class="name">(st)</td><td>static data, not dynamically retrieved</td></tr>
    <tr><td class="name">Evaluated</td><td>Requirements are evaluated against this value</td></tr>
    <tr><td class="name">Baseline</td><td>Baseline reference evaluated value</td></tr>
    <tr><td class="name">Current</td><td>This measurement's evaluated value, to be compared with baseline</td></tr>
    <tr><td class="name">Delta %</td><td>Comparison of evaluated values between current and baseline, relative to the baseline<br>
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
    <th class="blank"/><th class="blank"/><th class="blank"/><th class="blank"/><th class="blank"/><th class="blank">Evaluated</th><th class="blank"/><th class="blank"/><th class="blank"/><th class="blank"/><th class="blank"/><th class="blank">Baseline</th><th class="blank">Current</th><th class="blank"/>
    </tr>
    <tr valign="top">
    <th>Id</th><th>Transaction</th><th>Success</th><th>Min</th><th>Avg</th><th>90 perc</th><th>Max</th><th>StDev</th><th>Failed</th><th>Canceled</th><th class="blank"></th><th>v7.2.0.46</br>2016.04.18.13.47.02</th><th>v7.2.0.46</br>2016.04.19.02.44.48</th><th>Delta %</th>
    </tr>
    <tr valign="top" class="">
    <td>1</td><td class="name">Ingeschrevenen_01_Openen</td>
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
    <td>2</td><td class="name">Ingeschrevenen_02_Inloggen</td>
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
    <td>3</td><td class="name">Ingeschrevenen_03_WerkelijkInloggen</td>
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
    <td>4</td><td class="name">Ingeschrevenen_04_Inschrijven</td>
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
    <td>5</td><td class="name">Ingeschrevenen_05_Uitschrijven</td>
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
    <th>Id</th><th>Transaction</th><th>Success</th><th>Min</th><th>Avg</th><th>90 perc</th><th>Max</th><th>StDev</th><th>Failed</th><th>Canceled</th><th class="blank"></th><th>v7.2.0.46</br>2016.04.18.13.47.02</th><th>v7.2.0.46</br>2016.04.19.02.44.48</th><th>Delta %</th>
    </tr>
    <tr valign="top" class="">
    <td>6</td><td class="name">Beheerder_03_ZoekenHouder</td>
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
    <td>7</td><td class="name">Beheerder_04_PersoonInschrijven</td>
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
    <td>8</td><td class="name">Beheerder_05_Zoekenpersoon</td>
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
    <td>9</td><td class="name">Beheerder_06_Uitschrijven</td>
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
    <th>Id</th><th>Transaction</th><th>Success</th><th>Min</th><th>Avg</th><th>90 perc</th><th>Max</th><th>StDev</th><th>Failed</th><th>Canceled</th><th class="blank"></th><th>v7.2.0.46</br>2016.04.18.13.47.02</th><th>v7.2.0.46</br>2016.04.19.02.44.48</th><th>Delta %</th>
    </tr>

    <tr valign="top" class="">
    <td>10</td><td class="name">Houder_01_Openen</td>
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
    <td>11</td><td class="name">Houder_02_Inloggen</td>
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
    <td>12</td><td class="name">Houder_03_WerkelijkInloggen</td>
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
    <td>13</td><td class="name">Houder_04_Koppelen</td>
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
    <td>14</td><td class="name">Houder_05_OngedaanMaken</td>
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
    <td>15</td><td class="name">Houder_06_KoppelingenBekijken</td>
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
    <td>16</td><td class="name">Houder_07_OpenenKoppeling</td>
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
    <td>17</td><td class="name">Houder_99_Uitloggen</td>
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

<hr align="left" width="100%" size="1"/>

<h2>General</h2>
<div id="container_counters" style="min-width: 10px; height: 400px; margin: 0 auto"></div>

<h2>CPU</h2>
<div id="container_cpu_allservers" style="min-width: 310px; height: 400px; margin: 0 auto"></div>

<h2>Memory</h2>
<div id="container_dotnetclr_bytesinallheaps_allservers" style="min-width: 310px; height: 400px; margin: 0 auto"></div>
<div id="container_dotnetclr_timeingc_allservers" style="min-width: 310px; height: 400px; margin: 0 auto"></div>

<h2>ASP.NET</h2>
<div id="container_aspnet_requestsexecuting_allservers" style="min-width: 310px; height: 400px; margin: 0 auto"></div>
<div id="container_aspnet_requestsqueued_allservers" style="min-width: 310px; height: 400px; margin: 0 auto"></div>

<h2>Database</h2>
<div id="container_sqlserver_sqlservermetrics_allservers" style="min-width: 310px; height: 400px; margin: 0 auto"></div>

<hr align="left" width="100%" size="1">

<h3>end of report</h3>
</body></html>
"""


class YmorUnderTest(Ymor):
    """ Override the Ymor performance report to return the url as report contents. """
    # pylint: disable=unused-argument,no-self-use

    def url_open(self, url):
        """ Return the static html. """
        return HTML

    def urls(self, product, version):
        """ Return a list of urls for the performance report. """
        return ['http://report/1'] if product != 'product' else []


class JMeterTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the JMeter performance report metric source. """

    def setUp(self):
        self.__performance_report = YmorUnderTest('http://report/')

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual('http://report/', self.__performance_report.url())

    def test_queries_non_existing(self):
        """ Test that the number of queries for a product/version that is not found is zero. """
        self.assertEqual(0, self.__performance_report.queries('product', 'version'))

    def test_queries(self):
        """ Test that the total number of queries for a product/version that is in the report. """
        self.assertEqual(17, self.__performance_report.queries(('.*[0-9][0-9].*', 'dummy'), '12.5.5'))

    def test_queries_violating_max_responsetime(self):
        """ Test that the number of queries violating the maximum response times is zero. """
        self.assertEqual(0, self.__performance_report.queries_violating_max_responsetime(('.*[0-9][0-9].*', 'dummy'),
                                                                                         '12.5.5'))

    def test_queries_violating_wished_reponsetime(self):
        """ Test that the number of queries violating the wished response times is zero. """
        self.assertEqual(0, self.__performance_report.queries_violating_wished_responsetime(('.*[0-9][0-9].*', 'dummy'),
                                                                                            '12.5.5'))

    def test_date_of_last_measurement(self):
        """ Test that the date of the last measurement is correctly parsed from the report. """
        self.assertEqual(datetime.datetime(2016, 4, 19, 3, 27, 56),
                         self.__performance_report.date(('.*[0-9][0-9].*', 'dummy'), '12.5.5'))

    def test_date_product_not_found(self):
        """ Test the date when the product/version is not in the report. """
        self.assertEqual(datetime.datetime.min, self.__performance_report.date('product', 'version'))
