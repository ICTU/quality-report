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

import unittest
import StringIO
from qualitylib.metric_source import Sonar, Maven
from qualitylib.metric_source.sonar_runner import SonarRunner


class SonarRunnerUnderTest(SonarRunner):
    ''' Override SonarRunner to return a fake JSON string. '''
    def url_open(self, *args, **kwargs):  # pylint: disable=unused-argument
        ''' Return a fake JSON string. '''
        return StringIO.StringIO('{}')


class SonarRunnerTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the Sonar runner that creates and deletes Sonar 
        analyses. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__runner = SonarRunnerUnderTest(Sonar('http://sonar/'), Maven())

    def test_analyse_products(self):
        ''' Test that the runner analyses products. '''
        self.__runner.analyse_products(set())
