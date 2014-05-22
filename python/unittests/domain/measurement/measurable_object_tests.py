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
from qualitylib.domain.measurement.measurable import MeasurableObject
from qualitylib.domain import TechnicalDebtTarget


class MeasurableObjectTests(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the measurable object. '''
    def setUp(self):  # pylint: disable=invalid-name
        self.__measurable = MeasurableObject(targets={self.__class__: 100},
            low_targets={self.__class__: 50},
            technical_debt_targets={self.__class__: 
                                    TechnicalDebtTarget(100, 'explanation')})

    def test_no_target(self):
        ''' Test that there is no target for an unknown class. '''
        self.failIf(self.__measurable.target(''.__class__))

    def test_target(self):
        ''' Test the target for a known class. '''
        self.assertEqual(100, self.__measurable.target(self.__class__))

    def test_no_low_target(self):
        ''' Test that there is no low target for an unknown class. '''
        self.failIf(self.__measurable.low_target(''.__class__))

    def test_low_target(self):
        ''' Test the low target for a known class. '''
        self.assertEqual(50, self.__measurable.low_target(self.__class__))

    def test_no_technical_debt(self):
        ''' Test that there is no technical debt for an unknown class. '''
        self.failIf(self.__measurable.technical_debt_target(''.__class__))

    def test_technical_debt(self):
        ''' Test the technical debt for a known class. '''
        target = self.__measurable.technical_debt_target(self.__class__)
        self.assertEqual(100, target.target_value())
