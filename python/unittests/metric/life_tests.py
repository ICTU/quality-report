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

from qualitylib import domain, metric
from unittests.domain.measurement.fake import FakeSubject
import unittest



class LifeUniverseAndEverythingUnderTest(metric.LifeUniverseAndEverything):
    # pylint: disable=too-many-public-methods
    ''' Override LowerIsBetterMetric to implement abstract methods that are 
        needed for running the unit tests. '''
    pass


class LifeUniverseAndEverythingTest(unittest.TestCase):  
    # pylint: disable=too-many-public-methods
    ''' Test case for the LowerIsBetterMetric domain class. '''

    def setUp(self):  # pylint: disable=C0103
        self.__subject = FakeSubject()
        self.__subject.metric_source_id = lambda x: 'x'  # method not provided by FakeSubject
        self.__project = domain.Project()
        self.__metric = LifeUniverseAndEverythingUnderTest(subject=self.__subject, 
                                                     project=self.__project)


    def test_default_status(self):
        ''' Test that the default status is perfect. '''
        self.assertEqual('red', self.__metric.status())


