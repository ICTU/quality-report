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


class Street(object):
    ''' Class representing a development or test street. '''

    def __init__(self, name, job_regexp, target_art_stability=3, 
                 low_target_art_stability=7, perfect_art_stability=1):
        self.__name = name
        self.__job_regexp = job_regexp
        self.__target_art_stability = target_art_stability
        self.__low_target_art_stability = low_target_art_stability
        self.__perfect_art_stability = perfect_art_stability

    def __str__(self):
        ''' Return the id string of the street. '''
        return self.id_string()

    def name(self):
        ''' Return the name of the street. '''
        return self.__name

    def id_string(self):
        ''' Return an id string for the street. '''
        return self.__name.lower().replace(' ', '_')

    def regexp(self):
        ''' Return the regular expression that describes the CI-jobs of the
            street. '''
        return self.__job_regexp

    def target_art_stability(self):
        ''' Return after how many days not succeeding we consider an ART to
            be unstable. '''
        return self.__target_art_stability

    def low_target_art_stability(self):
        ''' Return after how many days not succeeding we consider an ART to
            be very unstable. '''
        return self.__low_target_art_stability

    def perfect_art_stability(self):
        ''' Return after how many days not succeeding we consider an ART to
            be not perfectly stable. '''
        return self.__perfect_art_stability
