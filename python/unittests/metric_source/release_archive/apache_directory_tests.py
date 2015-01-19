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
from qualitylib.metric_source import ApacheDirectory


DEFAULT_HTML = '''
<table><tr><th></th><th>Name</th><th>Last modified</th><th>Size</th><th>Description</th></tr>
<tr><th colspan="5"><hr></th></tr>
<tr><td></td><td><a href="LR-GIR-KO-R11-RC1.zip">LR-GIR-KO-R11-RC1.zip</a></td><td>16-Aug-2012 14:35  </td><td>470M</td></tr>
<tr><td></td><td><a href="LR-GIR-KO-R11-RC2.zip">LR-GIR-KO-R11-RC2.zip</a></td><td>10-Sep-2012 14:27  </td><td>469M</td></tr>
<tr><td></td><td><a href="LR-GIR-KO-R11-RC3.zip">LR-GIR-KO-R11-RC3.zip</a></td><td>28-Sep-2012 15:56  </td><td>471M</td></tr>
<tr><td></td><td><a href="LR-GIR-KO-R11-RC4.zip">LR-GIR-KO-R11-RC4.zip</a></td><td>19-Oct-2012 14:26  </td><td>472M</td></tr>
<tr><td></td><td><a href="LR-GIR-KO-R11-patch1.zip">LR-GIR-KO-R11-patch1.zip</a></td><td>15-Nov-2012 16:20  </td><td>479M</td></tr>
<tr><td></td><td><a href="LR-GIR-KO-R11-patch2.zip">LR-GIR-KO-R11-patch2.zip</a></td><td>26-Nov-2012 12:05  </td><td>479M</td></tr>
<tr><td><img src="/icons/folder.gif" alt="[DIR]"></td><td><a href="Old/">Old/</a></td><td>19-Oct-2012 14:54  </td><td>  - </td></tr>
<tr><th colspan="5"><hr></th></tr>
</table>
'''

class ApacheDirectoryUnderTest(ApacheDirectory):
    ''' Override ApacheDirectory to have soup() use a fixed HTML fragment. '''
    html = DEFAULT_HTML
    def soup(self, url):
        return BeautifulSoup.BeautifulSoup(self.html)
    

class ApacheDirectoryTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the ApacheDirectory class. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        self.__apache_directory = ApacheDirectoryUnderTest('Archive', 
                                                           'http://archive')
        
    def test_name(self):
        ''' Test that the name is correct. '''
        self.assertEqual('Archive', self.__apache_directory.name())
        
    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual('http://archive', self.__apache_directory.url())
        
    def test_most_recent(self):
        ''' Test that the date time of the most recent file is correct. '''
        self.assertEqual(datetime.datetime(2012, 11, 26, 12, 5),
                         self.__apache_directory.date_of_most_recent_file()) 
        