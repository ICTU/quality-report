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

from qualitylib import domain
import unittest


class ServiceTest(unittest.TestCase):  # pylint: disable=R0904
    ''' Unit tests for the Service domain class. '''
    def setUp(self):  # pylint: disable=C0103
        self.__service = domain.Service(None, 'SV', 'Service', 
                                        'java_melody_id', 'nagios_id', 
                                        'Nagios')
        
    def test_name(self):
        ''' Test that the service has a name. '''
        self.assertEqual('Service', self.__service.name())

    def test_short_name(self):
        ''' Test that the service has a short name. '''
        self.assertEqual('SV', self.__service.short_name())
        
    def test_repr(self):
        ''' Test that __repr__ uses the service name. '''
        self.assertEqual(self.__service.name(), repr(self.__service))
        
    def test_java_melody_id(self):
        ''' Test the JavaMelody id. '''
        self.assertEqual('java_melody_id', self.__service.java_melody())
        
    def test_nagios_server_id(self):
        ''' Test the Nagios server id. '''
        self.assertEqual('nagios_id', self.__service.nagios_server_id())
        
    def test_nagios(self):
        ''' Test getting the Nagios instance of the service. '''
        self.assertEqual('Nagios', self.__service.nagios())
