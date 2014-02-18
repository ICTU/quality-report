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


from qualitylib.domain.measurement.measurable import MeasurableObject


class Service(MeasurableObject):
    ''' Class representing a service provided by a project. '''
    def __init__(self, project, short_name, name, javamelody_id='', 
                 nagios_server_id='', nagios=None, dependencies=None,
                 technical_debt_targets=None):
        super(Service, self).__init__( \
            technical_debt_targets=technical_debt_targets)
        self.__project = project
        self.__short_name = short_name
        self.__name = name
        self.__javamelody = javamelody_id
        self.__nagios_server_id = nagios_server_id
        self.__nagios = nagios
        self.__dependencies = dependencies or []
        
    def __repr__(self):
        return self.name()
        
    def name(self):
        ''' Return the name of the service. '''
        return self.__name

    def short_name(self):
        ''' Return a short (two letter) abbreviation of the service name. '''
        return self.__short_name
    
    def java_melody(self):
        ''' Return the id of this service in JavaMelody. '''
        return self.__javamelody
    
    def nagios_server_id(self):
        ''' Return the id of this service in Nagios. '''
        return self.__nagios_server_id
    
    def nagios(self):
        ''' Return the Nagios instance to use for this services. '''
        return self.__nagios

    def dependencies(self):
        ''' Return the services this service is depending on. '''
        return self.__dependencies
