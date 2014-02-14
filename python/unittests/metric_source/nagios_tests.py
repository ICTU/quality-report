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
import unittest
from qualitylib.metric_source import Nagios


HOSTGROUP_AVAILABILITY_HTML = '''
    <td class="hostUP">90%</td>
    <div class="dataTitle">abc</div>
    <div><table></table></div>'''


SERVICE_AVAILABILITY_HTML = '''
    <TABLE BORDER=0 CLASS='data'>
        <TR><TH CLASS='data'>Host</TH><TH CLASS='data'>Service</TH><TH CLASS='data'>% Time OK</TH><TH CLASS='data'>% Time Warning</TH><TH CLASS='data'>% Time Unknown</TH><TH CLASS='data'>% Time Critical</TH><TH CLASS='data'>% Time Undetermined</TH></TR>
        <tr><td><a>ivb-ai</a></td><td><a>Broncheck</a></td><td CLASS='serviceOK'>99.215% (99.215%)</td><td CLASS='serviceWARNING'>0.000% (0.000%)</td><td CLASS='serviceUNKNOWN'>0.000% (0.000%)</td><td class='serviceCRITICAL'>0.785% (0.785%)</td><td class='dataOdd'>0.000%</td></tr>
        <tr><td><a>ivb-ivw</a></td><td><a>Broncheck</a></td><td CLASS='serviceOK'>95.635% (95.635%)</td><td CLASS='serviceWARNING'>0.000% (0.000%)</td><td CLASS='serviceUNKNOWN'>0.000% (0.000%)</td><td class='serviceCRITICAL'>4.365% (4.365%)</td><td class='dataEven'>0.000%</td></tr>
        <tr><td><a>ivb-nvwa</a></td><td><a>Broncheck</a></td><td CLASS='serviceOK'>99.805% (99.805%)</td><td CLASS='serviceWARNING'>0.000% (0.000%)</td><td CLASS='serviceUNKNOWN'>0.000% (0.000%)</td><td class='serviceCRITICAL'>0.195% (0.195%)</td><td class='dataOdd'>0.000%</td></tr>
        <tr><td><a>ivb-vrom</a></td><td><a>Broncheck</a></td><td CLASS='serviceOK'>0.000% (0.000%)</td><td CLASS='serviceWARNING'>0.000% (0.000%)</td><td CLASS='serviceUNKNOWN'>0.000% (0.000%)</td><td class='serviceCRITICAL'>100.000% (100.000%)</td><td class='dataEven'>0.000%</td></tr>
        <tr><td colspan='2'>Average</td><td CLASS='serviceOK'>73.664% (73.664%)</td><td CLASS='serviceWARNING'>0.000% (0.000%)</td><td CLASS='serviceUNKNOWN'>0.000% (0.000%)</td><td class='serviceCRITICAL'>26.336% (26.336%)</td><td class='dataOdd'>0.000%</td></tr>
    </table>'''

              
class NagiosUnderTest(Nagios):
    ''' Override the soup method to return a fixed HTML fragment. '''
    html = ''

    def soup(self, url):
        return BeautifulSoup.BeautifulSoup(self.html)
    

class NagiosTest(unittest.TestCase):  
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the Nagios class. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        self.__nagios = NagiosUnderTest('http://nagios/', 'username', 
                                        'password', ['abc'])
        self.__nagios.html = HOSTGROUP_AVAILABILITY_HTML
        
    def test_availability_url(self):
        ''' Test the availability report url. '''
        self.assertEqual('http://nagios/nagios//cgi-bin/avail.cgi?'
                         'show_log_entries=&hostgroup=abc&timeperiod=lastmonth&'
                         'rpttimeperiod=17x7', 
                         self.__nagios.availability_url())
        
    def test_number_of_servers(self):
        ''' Test how many servers Nagios is monitoring. '''
        self.assertEqual(0, self.__nagios.number_of_servers())
        
    def test_servers_per_group(self):
        ''' Test how many servers per group Nagios is monitoring. '''
        self.assertEqual({}, self.__nagios.number_of_servers_per_group())
        
    def test_average_availability(self):
        ''' Test average availability. '''
        self.assertEqual(90, self.__nagios.average_availability())


class NagiosServiceAvailabilityTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the Nagios class. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        self.__nagios = NagiosUnderTest('http://nagios/', 'username', 
                                        'password', [], 
                                        availability_via_service=True)
        self.__nagios.html = SERVICE_AVAILABILITY_HTML
        
    def test_service_availability(self):
        ''' Test the availability of an individual service. '''
        self.assertEqual(95.635, self.__nagios.service_availability('ivb-ivw'))
        