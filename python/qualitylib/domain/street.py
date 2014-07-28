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


class Street(MeasurableObject):
    ''' Class representing a development or test street. '''

    def __init__(self, job_regexp, responsible_teams=None, *args, **kwargs):
        super(Street, self).__init__(*args, **kwargs)
        self.__job_regexp = job_regexp
        self.__responsible_teams = responsible_teams or []

    def __eq__(self, other):
        return self.id_string() == other.id_string()

    def __str__(self):
        ''' Return the id string of the street. '''
        return self.id_string()

    def id_string(self):
        ''' Return an id string for the street. '''
        return self.name().lower().replace(' ', '_')

    def responsible_teams(self, metric_class=None):
        ''' Return the teams responsible for the street. '''
        return self.__responsible_teams

    def regexp(self):
        ''' Return the regular expression that describes the CI-jobs of the
            street. '''
        return self.__job_regexp
