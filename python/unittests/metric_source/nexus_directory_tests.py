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
from qualitylib.metric_source import NexusDirectory


DEFAULT_HTML = '''
<html>
  <head>
    <title>Index of /nexus/content/groups/public/nl/ictu/pim/av/releases/av-milieu-koppelvlak/</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <link rel="stylesheet" href="http://svn.lrk.org:8081/nexus//style/Sonatype-content.css?1.3.6" type="text/css" media="screen" title="no title" charset="utf-8">
  </head>
  <body>
    <h1>Index of /nexus/content/groups/public/nl/ictu/pim/av/releases/av-milieu-koppelvlak/</h1>
    <table cellspacing="10">
      <tr>
        <th align="left">Name</th>
        <th>Last Modified</th>
        <th>Size</th>
        <th>Description</th>
      </tr>
      <tr>
        <td>
          <a href="../">Parent Directory</a>
        </td>
      </tr>
      <tr>
        <td>
          <a href="maven-metadata.xml">maven-metadata.xml</a>
        </td>
            <td>
              Wed Nov 06 09:47:53 CET 2013
            </td>
            <td align="right">
                              660
                          </td>
            <td>
              &nbsp;
            </td>
          </tr>
                  <tr>
            <td>
                              <a href="maven-metadata.xml.md5">maven-metadata.xml.md5</a>
                          </td>
            <td>
              Wed Nov 06 09:47:53 CET 2013
            </td>
            <td align="right">
                              32
                          </td>
            <td>
              &nbsp;
            </td>
          </tr>
                  <tr>
            <td>
                              <a href="maven-metadata.xml.sha1">maven-metadata.xml.sha1</a>
                          </td>
            <td>
              Wed Nov 06 09:47:53 CET 2013
            </td>
            <td align="right">
                              40
                          </td>
            <td>
              &nbsp;
            </td>
          </tr>
                  <tr>
            <td>
                              <a href="1.1.0/">1.1.0/</a>
                          </td>
            <td>
              Wed Nov 06 09:47:52 CET 2013
            </td>
            <td align="right">
                              &nbsp;
                          </td>
            <td>
              &nbsp;
            </td>
          </tr>
                  <tr>
            <td>
                              <a href="1.2.0/">1.2.0/</a>
                          </td>
            <td>
              Wed Nov 06 09:47:53 CET 2013
            </td>
            <td align="right">
                              &nbsp;
                          </td>
            <td>
              &nbsp;
            </td>
          </tr>
                  <tr>
            <td>
                              <a href="1.3.0/">1.3.0/</a>
                          </td>
            <td>
              Wed Nov 06 09:47:52 CET 2013
            </td>
            <td align="right">
                              &nbsp;
                          </td>
            <td>
              &nbsp;
            </td>
          </tr>
                  <tr>
            <td>
                              <a href="1.4.0/">1.4.0/</a>
                          </td>
            <td>
              Wed Nov 06 09:47:53 CET 2013
            </td>
            <td align="right">
                              &nbsp;
                          </td>
            <td>
              &nbsp;
            </td>
          </tr>
                  <tr>
            <td>
                              <a href="1.4.1/">1.4.1/</a>
                          </td>
            <td>
              Wed Nov 06 09:47:53 CET 2013
            </td>
            <td align="right">
                              &nbsp;
                          </td>
            <td>
              &nbsp;
            </td>
          </tr>
                  <tr>
            <td>
                              <a href="1.5.0/">1.5.0/</a>
                          </td>
            <td>
              Wed Nov 06 09:47:53 CET 2013
            </td>
            <td align="right">
                              &nbsp;
                          </td>
            <td>
              &nbsp;
            </td>
          </tr>
                  <tr>
            <td>
                              <a href="1.5.1/">1.5.1/</a>
                          </td>
            <td>
              Wed Nov 06 09:47:53 CET 2013
            </td>
            <td align="right">
                              &nbsp;
                          </td>
            <td>
              &nbsp;
            </td>
          </tr>
                  <tr>
            <td>
                              <a href="1.6.0/">1.6.0/</a>
                          </td>
            <td>
              Wed Nov 06 09:47:53 CET 2013
            </td>
            <td align="right">
                              &nbsp;
                          </td>
            <td>
              &nbsp;
            </td>
          </tr>
                  <tr>
            <td>
                              <a href="1.6.1/">1.6.1/</a>
                          </td>
            <td>
              Wed Nov 06 09:47:52 CET 2013
            </td>
            <td align="right">
                              &nbsp;
                          </td>
            <td>
              &nbsp;
            </td>
          </tr>
                  <tr>
            <td>
                              <a href="TEST1/">TEST1/</a>
                          </td>
            <td>
              Wed Nov 06 09:47:52 CET 2013
            </td>
            <td align="right">
                              &nbsp;
                          </td>
            <td>
              &nbsp;
            </td>
          </tr>
                  <tr>
            <td>
                              <a href="TEST2/">TEST2/</a>
                          </td>
            <td>
              Wed Nov 06 09:47:53 CET 2013
            </td>
            <td align="right">
                              &nbsp;
                          </td>
            <td>
              &nbsp;
            </td>
          </tr>
            </table>
  </body>
</html>

'''

class NexusDirectoryUnderTest(NexusDirectory):
    ''' Override NexusDirectory to have soup() use a fixed HTML fragment. '''
    html = DEFAULT_HTML
    def soup(self, url):
        return BeautifulSoup.BeautifulSoup(self.html)
    

class NexusDirectoryTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the NexusDirectory class. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        self.__nexus_directory = NexusDirectoryUnderTest('Archive', 
                                                         'http://archive')
        
    def test_name(self):
        ''' Test that the name is correct. '''
        self.assertEqual('Archive', self.__nexus_directory.name())
        
    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual('http://archive', self.__nexus_directory.url())
        
    def test_most_recent(self):
        ''' Test that the date time of the most recent file is correct. '''
        self.assertEqual(datetime.datetime(2013, 11, 6, 9, 47, 53),
                         self.__nexus_directory.date_of_most_recent_file()) 
        